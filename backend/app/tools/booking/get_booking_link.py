from langchain_core.tools import BaseTool

from app.tools.builder import ToolBuilder


def build_get_booking_link_tool(booking_url: str, contact_email: str) -> BaseTool:
    def get_link() -> str:
        if not booking_url:
            return "BOOKING_UNAVAILABLE: no booking link configured. Offer to escalate instead."
        return (
            "Cadre has no self-serve calendar. To talk to an AI Strategist the user fills in the "
            f"contact form at {booking_url} (first name, last name, company, work email, optional "
            f"phone, how Cadre can help) or emails {contact_email}. The team replies to schedule "
            "the call. You can also send the request for them with `request_strategy_call` if "
            "they give you those details here."
        )

    return (
        ToolBuilder("get_booking_link")
        .describe(
            "How to book a call with a Cadre AI strategist: the official contact page and email. "
            "Call it when the user asks how to book, schedule, meet or talk to someone at Cadre."
        )
        .handler(get_link)
        .build()
    )
