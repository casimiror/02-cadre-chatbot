from uuid import uuid4

import pytest
from pydantic import ValidationError

from app.tools.booking.get_booking_link import build_get_booking_link_tool
from app.tools.booking.request_strategy_call import build_request_strategy_call_tool


class FakeContactRequests:
    def __init__(self) -> None:
        self.created: list[dict] = []

    def create(self, conversation_id, **fields):
        self.created.append({"conversation_id": conversation_id, **fields})


ARGS = {
    "first_name": "Ana",
    "last_name": "Diaz",
    "company": "Acme Builders",
    "email": "ana@acme.com",
    "message": "Automate our bid leveling",
}


def test_booking_link_points_to_contact_page_and_offers_request():
    result = build_get_booking_link_tool("https://cadre.ai/contact", "hello@gocadre.ai").invoke({})
    assert "https://cadre.ai/contact" in result and "hello@gocadre.ai" in result
    assert "request_strategy_call" in result


def test_booking_link_unconfigured():
    assert build_get_booking_link_tool("", "").invoke({}).startswith("BOOKING_UNAVAILABLE")


def test_request_strategy_call_stores_request_for_conversation():
    repo = FakeContactRequests()
    conversation_id = uuid4()
    result = build_request_strategy_call_tool(repo).invoke(
        ARGS, config={"configurable": {"conversation_id": str(conversation_id)}}
    )
    assert result.startswith("REQUEST_SENT")
    assert repo.created == [{"conversation_id": conversation_id, "phone": None, **ARGS}]


def test_request_strategy_call_rejects_bad_email():
    # Inside the graph ToolNode turns this into a tool message so the model asks again.
    repo = FakeContactRequests()
    with pytest.raises(ValidationError):
        build_request_strategy_call_tool(repo).invoke(
            {**ARGS, "email": "not-an-email"},
            config={"configurable": {"conversation_id": str(uuid4())}},
        )
    assert repo.created == []
