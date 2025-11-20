from typing import Optional
from sqlalchemy.orm import Mapped, mapped_column, DECIMAL, VARCHAR

from lesson2_structured.database.models.base import Base, TimestampMixin, TableNameMixin, str_255, int_pk

    
class Product(Base, TimestampMixin, TableNameMixin):
    product_id: Mapped[int_pk]
    title: Mapped[str_255]
    description: Mapped[Optional[str]] = mapped_column(VARCHAR(3000))
    price: Mapped[float] = mapped_column(DECIMAL(precision=16, scale=4))