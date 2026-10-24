"""Run the dataset through the support agent, score it, and keep one JSON per run.

With Langfuse configured the run goes through `run_experiment`: every case becomes a trace of the
real agent linked to a dataset run, with its scores attached, so runs can be compared in the
Langfuse UI. Without Langfuse it is a plain thread pool. Either way the JSON is the source the
/eval page reads.
"""

import secrets
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor
from datetime import UTC, datetime
from pathlib import Path
from threading import Lock

from langchain_core.language_models import BaseChatModel
from langfuse import Evaluation, get_client
from langfuse.langchain import CallbackHandler

from app.core.config import BACKEND_DIR, Settings
from app.core.llm import build_chat_model
from app.evals.agent_run import build_eval_agent, run_agent
from app.evals.checks import run_checks
from app.evals.dataset import EvalCase
from app.evals.judge import judge_answer
from app.evals.results import CaseResult, EvalRun, summarize, summarize_by_category
from app.evals.retrieval import RetrievedDoc, score_retrieval
from app.tools.knowledge.kb import KnowledgeBase

RUNS_DIR = BACKEND_DIR / "eval_runs"
DATASET_NAME = "cadre-support-eval"

Progress = Callable[[int, int, CaseResult], None]


class Evaluator:
    def __init__(self, settings: Settings, *, use_langfuse: bool = True) -> None:
        self.settings = settings
        self.kb = KnowledgeBase()
        self.agent = build_eval_agent(settings, self.kb)
        judge_settings = settings.model_copy(
            update={"llm_model": settings.eval_judge_model, "llm_temperature": 0.0}
        )
        self.judge: BaseChatModel = build_chat_model(judge_settings)
        self.use_langfuse = use_langfuse and settings.langfuse_enabled

    def evaluate_case(self, case: EvalCase) -> CaseResult:
        callbacks = [CallbackHandler()] if self.use_langfuse else []
        run = run_agent(self.agent, case.question, callbacks)
        sections = self.kb.search(case.question)
        index_docs = [RetrievedDoc(s.source, s.title, s.body) for s in sections]
        judge, judge_error = None, None
        if run.error is None:
            try:
                judge = judge_answer(self.judge, case, run)
            except Exception as exc:  # noqa: BLE001 - keep the case, report the judge failure
                judge_error = repr(exc)
        return CaseResult(
            case=case,
            reply=run.reply,
            blocked_by=run.blocked_by,
            tool_calls=run.tool_calls,
            index_retrieval=score_retrieval(case.keywords, case.expected_sources, index_docs),
            agent_retrieval=score_retrieval(case.keywords, case.expected_sources, run.retrieved),
            checks=run_checks(case, run),
            judge=judge,
            judge_error=judge_error,
            latency_s=run.latency_s,
        )

    def run(
        self, cases: list[EvalCase], *, concurrency: int = 4, on_progress: Progress | None = None
    ) -> EvalRun:
        run_id = datetime.now(UTC).strftime("%Y%m%d-%H%M%S-") + secrets.token_hex(2)
        started = datetime.now(UTC)
        done, lock = 0, Lock()

        def task(case: EvalCase) -> CaseResult:
            nonlocal done
            result = self.evaluate_case(case)
            with lock:
                done += 1
                if on_progress:
                    on_progress(done, len(cases), result)
            return result

        if self.use_langfuse:
            results, url = self._run_in_langfuse(run_id, cases, task, concurrency)
        else:
            with ThreadPoolExecutor(concurrency) as pool:
                results, url = list(pool.map(task, cases)), None

        order = {case.id: i for i, case in enumerate(cases)}
        results.sort(key=lambda r: order[r.case.id])
        return EvalRun(
            id=run_id,
            started_at=started,
            finished_at=datetime.now(UTC),
            bot_model=self.settings.llm_model,
            judge_model=self.settings.eval_judge_model,
            summary=summarize(results),
            by_category=summarize_by_category(results),
            results=results,
            langfuse_url=url,
        )

    def _run_in_langfuse(
        self,
        run_id: str,
        cases: list[EvalCase],
        task: Callable[[EvalCase], CaseResult],
        concurrency: int,
    ) -> tuple[list[CaseResult], str | None]:
        langfuse = get_client()
        _sync_dataset(langfuse, cases)
        by_id = {case.id: case for case in cases}
        items = [i for i in langfuse.get_dataset(DATASET_NAME).items if i.id in by_id]

        def lf_task(*, item, **_):
            return task(by_id[item.id]).model_dump(mode="json")

        experiment = langfuse.run_experiment(
            name=DATASET_NAME,
            run_name=run_id,
            description=f"bot {self.settings.llm_model}, judge {self.settings.eval_judge_model}",
            data=items,
            task=lf_task,
            evaluators=[_scores],
            max_concurrency=concurrency,
            metadata={"bot_model": self.settings.llm_model},
        )
        langfuse.flush()
        results = []
        for item_result in experiment.item_results:
            if item_result.output is None:  # the task raised; nothing to report for it
                continue
            result = CaseResult.model_validate(item_result.output)
            result.trace_id = item_result.trace_id
            results.append(result)
        return results, experiment.experiment_url


def _sync_dataset(langfuse, cases: list[EvalCase]) -> None:
    """Upsert the dataset and its items: the dataset file is the source of truth."""
    langfuse.create_dataset(
        name=DATASET_NAME, description="Cadre support agent evaluation (backend/app/evals)"
    )
    for case in cases:
        langfuse.create_dataset_item(
            dataset_name=DATASET_NAME,
            id=case.id,
            input={"question": case.question},
            expected_output={
                "reference_answer": case.reference_answer,
                "behavior": case.expected_behavior,
            },
            metadata=case.model_dump(exclude={"question", "reference_answer"}),
        )


def _scores(*, output, **_) -> list[Evaluation]:
    """Turn a CaseResult into Langfuse scores on the item's trace."""
    result = CaseResult.model_validate(output)
    scores = [
        Evaluation(name="passed", value=result.passed, data_type="BOOLEAN"),
        Evaluation(
            name="checks_passed",
            value=all(c.passed for c in result.checks),
            data_type="BOOLEAN",
            comment="; ".join(f"{c.name}: {c.detail}" for c in result.checks if not c.passed),
        ),
    ]
    if result.judge:
        scores += [
            Evaluation(name=name, value=value, comment=result.judge.feedback)
            for name, value in result.judge.scores.items()
        ]
    if retrieval := result.agent_retrieval:
        scores += [
            Evaluation(name="agent_mrr", value=retrieval.mrr),
            Evaluation(name="agent_keyword_coverage", value=retrieval.keyword_coverage),
        ]
    return scores


def save_run(run: EvalRun, directory: Path = RUNS_DIR) -> Path:
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / f"{run.id}.json"
    path.write_text(run.model_dump_json(indent=2))
    return path
