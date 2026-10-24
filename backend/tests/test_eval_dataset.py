import re
from collections import Counter
from typing import get_args

import pytest

from app.evals.dataset import Category, load_dataset
from app.tools.knowledge.kb import KNOWLEDGE_DIR

CASES = load_dataset()
TOOLS = {"search_knowledge", "get_booking_link", "request_strategy_call", "escalate_to_human"}


def _normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text).lower()


KB = {p.stem: _normalize(p.read_text()) for p in KNOWLEDGE_DIR.glob("*.md")}


def test_five_cases_per_category():
    counts = Counter(c.category for c in CASES)
    assert counts == {category: 5 for category in get_args(Category)}


def test_ids_are_unique():
    assert len({c.id for c in CASES}) == len(CASES)


def test_all_six_brief_scenarios_are_covered():
    assert {c.scenario for c in CASES if c.scenario} == {1, 2, 3, 4, 5, 6}


@pytest.mark.parametrize("case", [c for c in CASES if c.keywords], ids=lambda c: c.id)
def test_keywords_exist_in_expected_sources(case):
    """Keeps the dataset honest when the knowledge base changes."""
    assert case.expected_sources, "keywords need the files they come from"
    text = " ".join(KB[source] for source in case.expected_sources)
    missing = [k for k in case.keywords if _normalize(k) not in text]
    assert not missing, f"not in {case.expected_sources}: {missing}"


@pytest.mark.parametrize("case", CASES, ids=lambda c: c.id)
def test_expected_tools_exist(case):
    assert set(case.expected_tools) <= TOOLS
