from app.db.daos.base_dao import BaseDAO
from app.db.models import EscalationRow


class EscalationDAO(BaseDAO[EscalationRow]):
    model = EscalationRow
