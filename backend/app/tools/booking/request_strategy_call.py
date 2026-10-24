from uuid import UUID

from langchain_core.runnables import RunnableConfig
from langchain_core.tools import BaseTool
from pydantic import BaseModel, EmailStr, Field

from app.repositories.contact_request_repository import ContactRequestRepository
from app.tools.builder import ToolBuilder


class RequestStrategyCallArgs(BaseModel):
    first_name: str = Field(description="User's first name, as they gave it", min_length=1)
    last_name: str = Field(description="User's last name, as they gave it", min_length=1)
    company: str = Field(description="User's company name", min_length=1)
    email: EmailStr = Field(description="User's work email, asked for explicitly")
    message: str = Field(
        description="How Cadre can help: the user's goal or problem, in their words", min_length=1
    )
    phone: str | None = Field(default=None, description="Phone number, only if the user gave it")


def build_request_strategy_call_tool(requests: ContactRequestRepository) -> BaseTool:
    def request_call(
        first_name: str,
        last_name: str,
        company: str,
        email: str,
        message: str,
        config: RunnableConfig,
        phone: str | None = None,
    ) -> str:
        conversation_id = UUID(config["configurable"]["conversation_id"])
        requests.create(
            conversation_id,
            first_name=first_name,
            last_name=last_name,
            company=company,
            email=email,
            phone=phone,
            message=message,
        )
        return (
            f"REQUEST_SENT: the Cadre team has the strategy-call request and will email {email} "
            "to schedule it."
        )

    return (
        ToolBuilder("request_strategy_call")
        .describe(
            "Send a request to talk to a Cadre AI strategist on the user's behalf, the same as "
            "the contact form. Only call it after the user agreed and gave first name, last name, "
            "company, work email and what they need help with; never guess a field."
        )
        .args(RequestStrategyCallArgs)
        .handler(request_call)
        .build()
    )
