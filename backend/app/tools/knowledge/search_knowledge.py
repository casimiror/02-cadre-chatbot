from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field

from app.tools.builder import ToolBuilder
from app.tools.knowledge.kb import KnowledgeBase


class SearchKnowledgeArgs(BaseModel):
    query: str = Field(
        description="What the user wants to know, as a few English keywords (the KB is in English)"
    )


def build_search_knowledge_tool(kb: KnowledgeBase) -> BaseTool:
    def search(query: str) -> str:
        sections = kb.search(query)
        if not sections:
            return "NO_RESULTS: the knowledge base has nothing on this. Offer to escalate."
        return "\n\n".join(s.render() for s in sections)

    return (
        ToolBuilder("search_knowledge")
        .describe(
            "Search Cadre AI's official knowledge base: company, services, industries, case "
            "studies, AI Maturity Index, portal, getting started, and Cadre's approach to AI "
            "governance, agent design, retrieval, model selection, security and guardrails, "
            "evaluation and compliance. Always use it before answering a factual question about "
            "Cadre; search again with other keywords if the first results don't answer it."
        )
        .args(SearchKnowledgeArgs)
        .handler(search)
        .build()
    )
