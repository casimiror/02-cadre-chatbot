"""The only place where concrete classes are wired together."""

from functools import lru_cache

from app.agents.support_agent import build_support_agent
from app.core.config import get_settings
from app.core.llm import build_chat_model
from app.db.daos.contact_request_dao import ContactRequestDAO
from app.db.daos.conversation_dao import ConversationDAO
from app.db.daos.escalation_dao import EscalationDAO
from app.db.daos.message_dao import MessageDAO
from app.db.session import build_session_factory
from app.repositories.contact_request_repository import ContactRequestRepository
from app.repositories.conversation_repository import ConversationRepository
from app.repositories.escalation_repository import EscalationRepository
from app.services.chat_service import ChatService
from app.tools.knowledge.kb import KnowledgeBase
from app.tools.registry import ToolDeps, build_support_tools


@lru_cache
def get_chat_service() -> ChatService:
    settings = get_settings()
    sessions = build_session_factory(settings)

    conversations = ConversationRepository(ConversationDAO(sessions), MessageDAO(sessions))
    escalations = EscalationRepository(EscalationDAO(sessions))
    contact_requests = ContactRequestRepository(ContactRequestDAO(sessions))

    tools = build_support_tools(ToolDeps(settings, KnowledgeBase(), escalations, contact_requests))
    agent = build_support_agent(build_chat_model(settings), tools, settings)
    return ChatService(conversations, agent, settings.max_history_messages)
