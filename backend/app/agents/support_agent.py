from langchain_core.language_models import BaseChatModel
from langchain_core.tools import BaseTool
from langgraph.graph.state import CompiledStateGraph

from app.agents.builder import AgentBuilder
from app.core.config import Settings
from app.guardrails.input import MaxLengthGuardrail, PromptInjectionGuardrail
from app.guardrails.output import AllowedLinksGuardrail, NoInventedPricesGuardrail


def build_support_agent(
    llm: BaseChatModel, tools: list[BaseTool], settings: Settings
) -> CompiledStateGraph:
    return (
        AgentBuilder("cadre-support")
        .with_llm(llm)
        .with_prompt_file("support.md")
        .with_tools(tools)
        .with_input_guardrails(
            [MaxLengthGuardrail(settings.max_input_chars), PromptInjectionGuardrail()]
        )
        .with_output_guardrails(
            [
                NoInventedPricesGuardrail(),
                AllowedLinksGuardrail(
                    [settings.booking_url, settings.portal_url, settings.website_url]
                ),
            ]
        )
        .build()
    )
