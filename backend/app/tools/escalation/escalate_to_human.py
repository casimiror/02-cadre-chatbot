from uuid import UUID

from langchain_core.runnables import RunnableConfig
from langchain_core.tools import BaseTool
from pydantic import BaseModel, EmailStr, Field

from app.repositories.escalation_repository import EscalationRepository
from app.tools.builder import ToolBuilder


class EscalateArgs(BaseModel):
    email: EmailStr = Field(description="User's email, asked for explicitly")
    question: str = Field(description="The question the bot could not answer, in the user's words")
    name: str | None = Field(default=None, description="User's name if they gave it")


def build_escalate_to_human_tool(escalations: EscalationRepository) -> BaseTool:
    def escalate(email: str, question: str, config: RunnableConfig, name: str | None = None) -> str:
        conversation_id = UUID(config["configurable"]["conversation_id"])
        escalations.create(conversation_id, email=email, question=question, name=name)
        return "ESCALATED: the Cadre team has the question and will reply by email."

    return (
        ToolBuilder("escalate_to_human")
        .describe(
            "Hand the conversation to the Cadre team when you can't answer from the knowledge "
            "base, or the user asks for a person. Only call it after the user gave their email."
        )
        .args(EscalateArgs)
        .handler(escalate)
        .build()
    )
