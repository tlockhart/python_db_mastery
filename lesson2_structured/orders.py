# Step2: Table Creation
from sqlalchemy.orm import Mapped

from lesson2_structured.database.models.base import Base, TimestampMixin, TableNameMixin, int_pk, user_fk


class Order(Base, TimestampMixin, TableNameMixin):
    order_id: Mapped[int_pk]
    user_id: Mapped[user_fk]