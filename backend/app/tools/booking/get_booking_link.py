from langchain_core.tools import BaseTool

from app.tools.builder import ToolBuilder


def build_get_booking_link_tool(booking_url: str) -> BaseTool:
    def get_link() -> str:
        if not booking_url:
            return "BOOKING_UNAVAILABLE: no booking link configured. Offer to escalate instead."
        return f"Booking link for a call with a Cadre AI strategist: {booking_url}"

    return (
        ToolBuilder("get_booking_link")
        .describe("Get the official link to book a strategy call with a Cadre AI strategist.")
        .handler(get_link)
        .build()
    )
