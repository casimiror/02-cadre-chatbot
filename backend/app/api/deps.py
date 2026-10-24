"""The only place where concrete classes are wired together."""

from functools import lru_cache
from typing import TYPE_CHECKING

from sqlalchemy.orm import Session, sessionmaker

from app.agents.support_agent import build_support_agent
from app.core.config import get_settings
from app.core.llm import build_chat_model
from app.db.daos.contact_request_dao import ContactRequestDAO
from app.db.daos.conversation_dao import ConversationDAO
from app.db.daos.escalation_dao import EscalationDAO
from app.db.daos.message_dao import MessageDAO
from app.db.daos.message_feedback_dao import MessageFeedbackDAO
from app.db.session import build_session_factory
from app.repositories.contact_request_repository import ContactRequestRepository
from app.repositories.conversation_repository import ConversationRepository
from app.repositories.escalation_repository import EscalationRepository
from app.repositories.feedback_repository import FeedbackRepository
from app.services.chat_service import ChatService
from app.services.feedback_service import FeedbackService
from app.tools.knowledge.kb import KnowledgeBase
from app.tools.registry import ToolDeps, build_support_tools

if TYPE_CHECKING:
    from app.services.eval_service import EvalService


@lru_cache
def get_sessions() -> sessionmaker[Session]:
    """One engine per process, shared by every service."""
    return build_session_factory(get_settings())


@lru_cache
def get_chat_service() -> ChatService:
    settings = get_settings()
    sessions = get_sessions()

    conversations = ConversationRepository(ConversationDAO(sessions), MessageDAO(sessions))
    escalations = EscalationRepository(EscalationDAO(sessions))
    contact_requests = ContactRequestRepository(ContactRequestDAO(sessions))

    tools = build_support_tools(ToolDeps(settings, KnowledgeBase(), escalations, contact_requests))
    agent = build_support_agent(build_chat_model(settings), tools, settings)
    return ChatService(conversations, agent, settings.max_history_messages)


@lru_cache
def get_feedback_service() -> FeedbackService:
    sessions = get_sessions()
    return FeedbackService(FeedbackRepository(MessageDAO(sessions), MessageFeedbackDAO(sessions)))


@lru_cache
def get_eval_service() -> "EvalService":
    """Local-only: the router is mounted when EVAL_ENABLED is true. Imports stay inside so the
    deployed app never loads the evaluator."""
    from app.evals.runner import Evaluator
    from app.evals.store import RunStore
    from app.services.eval_service import EvalService

    return EvalService(lambda: Evaluator(get_settings()), RunStore())
