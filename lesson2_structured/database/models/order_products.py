# Step2: Table Creation
from sqlalchemy.orm import Mapped, mapped_column, relationship


from lesson2_structured.database.models.base import Base, TableNameMixin
from .products import Product

from sqlalchemy import Integer,ForeignKey



class OrderProduct(Base, TableNameMixin):
    """
    Summary: Connect orders and products table.  Will have one product at a time

    Args:
        Base (_type_): _description_
        TableNameMixin (_type_): _description_
    """
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
    
    product: Mapped["Product"] = relationship()