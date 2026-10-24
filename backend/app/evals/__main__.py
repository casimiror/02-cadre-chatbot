"""CLI: `make eval args="..."` (python -m app.evals)."""

import argparse
import sys
from typing import get_args

from app.core import observability
from app.core.config import get_settings
from app.evals.dataset import Category, load_dataset
from app.evals.results import CaseResult
from app.evals.runner import Evaluator, save_run


def _progress(done: int, total: int, result: CaseResult) -> None:
    mark = "PASS" if result.passed else "FAIL"
    print(f"[{done:>2}/{total}] {mark} {result.case.id}", flush=True)


def main() -> int:
    parser = argparse.ArgumentParser(description="Evaluate the support agent on the dataset.")
    parser.add_argument("--category", action="append", choices=get_args(Category))
    parser.add_argument("--id", action="append", dest="ids", help="case id, repeatable")
    parser.add_argument("--limit", type=int)
    parser.add_argument("--concurrency", type=int, default=4)
    parser.add_argument("--no-langfuse", action="store_true")
    args = parser.parse_args()

    cases = load_dataset()
    if args.category:
        cases = [c for c in cases if c.category in args.category]
    if args.ids:
        cases = [c for c in cases if c.id in args.ids]
    cases = cases[: args.limit] if args.limit else cases
    if not cases:
        print("no cases match", file=sys.stderr)
        return 1

    settings = get_settings()
    observability.init_observability(settings)
    evaluator = Evaluator(settings, use_langfuse=not args.no_langfuse)
    run = evaluator.run(cases, concurrency=args.concurrency, on_progress=_progress)
    path = save_run(run)

    s = run.summary
    print(f"\nrun {run.id}: {s.cases} cases, pass rate {s.pass_rate:.0%}")
    print(f"judge: {', '.join(f'{k} {v:.2f}' for k, v in s.judge.items())}")
    for label, metrics in (("index", s.index_retrieval), ("agent", s.agent_retrieval)):
        if metrics:
            print(f"{label} retrieval: {', '.join(f'{k} {v:.2f}' for k, v in metrics.items())}")
    print(f"saved {path.relative_to(path.parents[1])}")
    if run.langfuse_url:
        print(f"langfuse: {run.langfuse_url}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
