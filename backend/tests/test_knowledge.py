import re

import pytest

from app.guardrails.output import AllowedLinksGuardrail, NoInventedPricesGuardrail
from app.tools.knowledge.kb import KNOWLEDGE_DIR, KnowledgeBase
from app.tools.knowledge.search_knowledge import build_search_knowledge_tool


@pytest.fixture(scope="module")
def kb() -> KnowledgeBase:
    return KnowledgeBase()


def test_title_match_outranks_passing_mention(tmp_path):
    (tmp_path / "a.md").write_text(
        "# A\n## Pricing\nDepends on scope.\n"
        "## Services\nStrategy and engineering. Pricing is mentioned here in passing, along with "
        "many other words about services, industries, partners and outcomes.\n"
    )
    assert KnowledgeBase(tmp_path).search("pricing")[0].title == "Pricing"


def test_plurals_match_singular(tmp_path):
    (tmp_path / "a.md").write_text("# A\n## Industries\nConstruction and retail.\n")
    assert KnowledgeBase(tmp_path).search("industry")


def test_header_before_first_section_is_not_indexed(tmp_path):
    (tmp_path / "a.md").write_text("# A\n<!-- Source: secret notes -->\n## Hours\n9 to 5.\n")
    assert KnowledgeBase(tmp_path).search("secret notes") == []


@pytest.mark.parametrize(
    ("query", "expected"),
    [
        ("industries construction", "industries-and-departments"),
        ("book call strategist", "faq"),
        ("client portal access", "faq"),
        ("AI Maturity Index scored", "ai-maturity-index"),
        ("LLM selection data security", "security-and-guardrails"),
        ("prompt injection guardrails", "security-and-guardrails"),
        ("governance roles ownership", "ai-governance"),
        ("agent human in the loop", "agent-design"),
        ("RAG retrieval chunking", "retrieval-and-knowledge"),
        ("evaluation quality dimensions", "evaluation-and-production"),
        ("compliance GDPR HIPAA", "compliance"),
        ("model tiers Haiku Opus", "model-selection"),
        ("case study loan assistant", "case-studies"),
    ],
)
def test_scenario_queries_hit_the_right_document(kb, query, expected):
    assert kb.search(query)[0].source == expected


def test_no_results_code(kb):
    assert build_search_knowledge_tool(kb).invoke({"query": "zzz qqq"}).startswith("NO_RESULTS")


def test_knowledge_passes_output_guardrails():
    # The bot quotes the KB verbatim; a "$" amount or a raw URL would get the answer replaced.
    for path in KNOWLEDGE_DIR.glob("*.md"):
        text = re.sub(r"<!--.*?-->", "", path.read_text(), flags=re.DOTALL)
        assert NoInventedPricesGuardrail().check(text).allowed, path.name
        assert AllowedLinksGuardrail([]).check(text).allowed, path.name
