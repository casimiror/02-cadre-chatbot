import time

import pytest

from app.evals.store import RunStore
from app.services.eval_service import EvalBusyError, EvalService


class FakeEvaluator:
    def __init__(self, delay: float = 0) -> None:
        self.delay = delay

    def run_retrieval(self, cases, *, on_progress):
        from datetime import UTC, datetime

        from app.evals.results import RetrievalRun, RetrievalSummary

        for i, _ in enumerate(cases, start=1):
            time.sleep(self.delay)
            on_progress(i, len(cases))
        perfect = {"mrr": 1, "ndcg": 1, "keyword_coverage": 1, "source_hit": 1}
        summary = RetrievalSummary(cases=len(cases), **perfect)
        now = datetime.now(UTC)
        return RetrievalRun(
            id="retrieval-20261024-120000-abcd",
            started_at=now,
            finished_at=now,
            summary=summary,
            by_category={},
            results=[],
        )


def _wait(service, job_id):
    for _ in range(100):
        job = service.get(job_id)
        if job.status != "running":
            return job
        time.sleep(0.01)
    raise AssertionError("job did not finish")


def test_run_finishes_and_is_stored(tmp_path):
    store = RunStore(tmp_path)
    service = EvalService(FakeEvaluator, store)
    job = _wait(service, service.start("retrieval", ["direct_fact"]).id)
    assert (job.status, job.done, job.total) == ("done", 5, 5)
    assert store.get(job.run_id).summary.mrr == 1
    assert [r.id for r in store.list("retrieval")] == [job.run_id]


def test_only_one_run_at_a_time(tmp_path):
    service = EvalService(lambda: FakeEvaluator(delay=0.05), RunStore(tmp_path))
    first = service.start("retrieval", ["direct_fact"])
    with pytest.raises(EvalBusyError):
        service.start("retrieval")
    _wait(service, first.id)


def test_failures_are_reported(tmp_path):
    def broken():
        raise RuntimeError("no key")

    service = EvalService(broken, RunStore(tmp_path))
    job = _wait(service, service.start("answer", ["guardrail"]).id)
    assert job.status == "failed" and "no key" in job.error


@pytest.mark.parametrize("bad", ["../../etc/passwd", "retrieval-x", "answer-2026"])
def test_store_rejects_ids_that_are_not_run_ids(tmp_path, bad):
    assert RunStore(tmp_path).get(bad) is None
