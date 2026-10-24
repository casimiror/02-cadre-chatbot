from app.db.daos.base_dao import BaseDAO
from app.db.models import ContactRequestRow


class ContactRequestDAO(BaseDAO[ContactRequestRow]):
    model = ContactRequestRow
