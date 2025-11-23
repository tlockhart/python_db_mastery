# Step2: Table Creation
from sqlalchemy.orm import Mapped, mapped_column

from lesson2_structured.database.models.base import Base, TableNameMixin
from sqlalchemy import Integer,ForeignKey

class OrderProduct(Base, TableNameMixin):
    order_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey('orders.order_id', ondelete="CASCADE"),
        primary_key=True
    )
    product_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey('products.product_id', ondelete="CASCADE"),
        primary_key=True
    )
    quantity: Mapped[int]