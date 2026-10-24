from uuid import UUID

from app.db.daos.contact_request_dao import ContactRequestDAO
from app.domain.models import ContactRequest


class ContactRequestRepository:
    def __init__(self, requests: ContactRequestDAO) -> None:
        self._requests = requests

    def create(
        self,
        conversation_id: UUID,
        *,
        first_name: str,
        last_name: str,
        company: str,
        email: str,
        message: str,
        phone: str | None = None,
    ) -> ContactRequest:
        row = self._requests.insert(
            conversation_id=conversation_id,
            first_name=first_name,
            last_name=last_name,
            company=company,
            email=email,
            phone=phone,
            message=message,
        )
        return ContactRequest.model_validate(row, from_attributes=True)
