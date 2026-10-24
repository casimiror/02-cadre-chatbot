from dataclasses import dataclass
from uuid import UUID

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage
from langgraph.graph.state import CompiledStateGraph

from app.core.observability import trace_turn
from app.domain.models import Message
from app.repositories.conversation_repository import ConversationRepository


@dataclass(frozen=True)
class TurnResult:
    conversation_id: UUID
    message_id: UUID  # the stored assistant message, the target of 👍/👎 feedback
    reply: str
    blocked_by: str | None


def _to_langchain(history: list[Message]) -> list[BaseMessage]:
    return [HumanMessage(m.content) if m.role == "user" else AIMessage(m.content) for m in history]


class ChatService:
    def __init__(
        self, conversations: ConversationRepository, agent: CompiledStateGraph, history_limit: int
    ) -> None:
        self._conversations = conversations
        self._agent = agent
        self._history_limit = history_limit

    def handle_turn(
        self, conversation_id: UUID | None, user_text: str, visitor_id: UUID | None = None
    ) -> TurnResult:
        conversation = self._conversations.get_or_create(conversation_id, visitor_id)
        history = self._conversations.recent_messages(conversation.id, self._history_limit)

        # The stored visitor wins, so one conversation is never split across Langfuse users.
        visitor = conversation.visitor_id or visitor_id
        user_id = str(visitor) if visitor else None
        with trace_turn(str(conversation.id), user_id, user_text) as trace:
            config = {**trace.config, "configurable": {"conversation_id": str(conversation.id)}}
            state = self._agent.invoke(
                {"messages": [*_to_langchain(history), HumanMessage(user_text)]}, config
            )
            reply = state["messages"][-1].text
            trace.finish(reply, state.get("blocked_by"))

        # Persist only after a successful turn so a failed LLM call leaves no half-turn.
        self._conversations.append(conversation.id, "user", user_text)
        answer = self._conversations.append(conversation.id, "assistant", reply)
        return TurnResult(conversation.id, answer.id, reply, state.get("blocked_by"))
