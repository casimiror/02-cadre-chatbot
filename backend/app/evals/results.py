"""What one evaluation run produces. Serialized as one JSON file per run."""

from collections import defaultdict
from datetime import datetime
from statistics import mean

from pydantic import BaseModel

from app.evals.agent_run import ToolCall
from app.evals.checks import Check
from app.evals.dataset import EvalCase
from app.evals.judge import AnswerEval
from app.evals.retrieval import RetrievalMetrics

# A case passes when every deterministic check passes and the judge gives at least this
# accuracy and behaviour (1-5). Same "acceptable" bar as the course's amber threshold.
PASS_SCORE = 4


class CaseResult(BaseModel):
    case: EvalCase
    reply: str
    blocked_by: str | None
    tool_calls: list[ToolCall]
    index_retrieval: RetrievalMetrics | None  # kb.search(question): the index alone
    agent_retrieval: RetrievalMetrics | None  # what the agent's own searches returned
    checks: list[Check]
    judge: AnswerEval | None
    judge_error: str | None = None
    latency_s: float
    trace_id: str | None = None

    @property
    def passed(self) -> bool:
        checks_ok = all(c.passed for c in self.checks)
        judge_ok = self.judge is not None and min(self.judge.accuracy, self.judge.behavior) >= (
            PASS_SCORE
        )
        return checks_ok and judge_ok


class Summary(BaseModel):
    cases: int
    pass_rate: float
    checks_pass_rate: float
    index_retrieval: dict[str, float]  # mrr, ndcg, keyword_coverage, source_hit
    agent_retrieval: dict[str, float]
    judge: dict[str, float]  # mean of each 1-5 score
    latency_s: float


class EvalRun(BaseModel):
    id: str
    started_at: datetime
    finished_at: datetime
    bot_model: str
    judge_model: str
    summary: Summary
    by_category: dict[str, Summary]
    results: list[CaseResult]
    langfuse_url: str | None = None


def _retrieval_means(metrics: list[RetrievalMetrics | None]) -> dict[str, float]:
    present = [m for m in metrics if m is not None]
    if not present:
        return {}
    return {
        "mrr": mean(m.mrr for m in present),
        "ndcg": mean(m.ndcg for m in present),
        "keyword_coverage": mean(m.keyword_coverage for m in present),
        "source_hit": mean(1.0 if m.source_hit else 0.0 for m in present),
    }


def summarize(results: list[CaseResult]) -> Summary:
    judged = [r.judge for r in results if r.judge]
    checks = [c.passed for r in results for c in r.checks]
    return Summary(
        cases=len(results),
        pass_rate=mean(1.0 if r.passed else 0.0 for r in results),
        checks_pass_rate=mean(1.0 if ok else 0.0 for ok in checks) if checks else 0.0,
        index_retrieval=_retrieval_means([r.index_retrieval for r in results]),
        agent_retrieval=_retrieval_means([r.agent_retrieval for r in results]),
        judge={k: mean(j.scores[k] for j in judged) for k in judged[0].scores} if judged else {},
        latency_s=mean(r.latency_s for r in results),
    )


def summarize_by_category(results: list[CaseResult]) -> dict[str, Summary]:
    groups: dict[str, list[CaseResult]] = defaultdict(list)
    for r in results:
        groups[r.case.category].append(r)
    return {category: summarize(group) for category, group in groups.items()}
