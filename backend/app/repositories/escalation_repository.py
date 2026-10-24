from uuid import UUID

from app.db.daos.escalation_dao import EscalationDAO
from app.domain.models import Escalation


class EscalationRepository:
    def __init__(self, escalations: EscalationDAO) -> None:
        self._escalations = escalations

    def create(
        self, conversation_id: UUID, email: str, question: str, name: str | None = None
    ) -> Escalation:
        row = self._escalations.insert(
            conversation_id=conversation_id, email=email, name=name, question=question
        )
        return Escalation.model_validate(row, from_attributes=True)
