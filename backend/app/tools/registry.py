from dataclasses import dataclass

from langchain_core.tools import BaseTool

from app.core.config import Settings
from app.repositories.contact_request_repository import ContactRequestRepository
from app.repositories.escalation_repository import EscalationRepository
from app.tools.booking.get_booking_link import build_get_booking_link_tool
from app.tools.booking.request_strategy_call import build_request_strategy_call_tool
from app.tools.escalation.escalate_to_human import build_escalate_to_human_tool
from app.tools.knowledge.kb import KnowledgeBase
from app.tools.knowledge.search_knowledge import build_search_knowledge_tool


@dataclass(frozen=True)
class ToolDeps:
    settings: Settings
    kb: KnowledgeBase
    escalations: EscalationRepository
    contact_requests: ContactRequestRepository


def build_support_tools(deps: ToolDeps) -> list[BaseTool]:
    """Every tool the support agent can call. Add new tools here."""
    return [
        build_search_knowledge_tool(deps.kb),
        build_get_booking_link_tool(deps.settings.booking_url, deps.settings.contact_email),
        build_request_strategy_call_tool(deps.contact_requests),
        build_escalate_to_human_tool(deps.escalations),
    ]
