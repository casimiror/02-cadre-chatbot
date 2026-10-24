from dataclasses import dataclass
from uuid import UUID

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage
from langgraph.graph.state import CompiledStateGraph

from app.core.observability import trace_config
from app.domain.models import Message
from app.repositories.conversation_repository import ConversationRepository


@dataclass(frozen=True)
class TurnResult:
    conversation_id: UUID
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

    def handle_turn(self, conversation_id: UUID | None, user_text: str) -> TurnResult:
        conversation = self._conversations.get_or_create(conversation_id)
        history = self._conversations.recent_messages(conversation.id, self._history_limit)

        config = trace_config(str(conversation.id))
        config["configurable"] = {"conversation_id": str(conversation.id)}
        state = self._agent.invoke(
            {"messages": [*_to_langchain(history), HumanMessage(user_text)]}, config
        )
        reply = state["messages"][-1].text

        # Persist only after a successful turn so a failed LLM call leaves no half-turn.
        self._conversations.append(conversation.id, "user", user_text)
        self._conversations.append(conversation.id, "assistant", reply)
        return TurnResult(conversation.id, reply, state.get("blocked_by"))
