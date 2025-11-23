# Step2: Table Creation
from sqlalchemy.orm import Mapped, relationship
from .order_products import OrderProduct
from .users import User

from lesson2_structured.database.models.base import Base, TimestampMixin, TableNameMixin, int_pk, user_fk


class Order(Base, TimestampMixin, TableNameMixin):
    order_id: Mapped[int_pk]
    user_id: Mapped[user_fk]
    
    # Association
    products: Mapped[list["OrderProduct"]] = relationship()
    user: Mapped["User"] = relationship(
        "User", back_populates="orders"
    )