# Step2: Table Creation
from typing import Optional
from sqlalchemy.orm import Mapped, mapped_column

from sqlalchemy import BIGINT, VARCHAR

from lesson2_structured.database.models.base import Base, TimestampMixin, TableNameMixin, str_255, user_fk
from .orders import Order

from sqlalchemy.orm import relationship


# USER WITH TYPE ALLIASES:
class User(Base, TimestampMixin, TableNameMixin):
    telegram_id: Mapped[int] = mapped_column(
        BIGINT, primary_key=True, autoincrement=False
    )
    full_name: Mapped[str_255]
    user_name: Mapped[Optional[str_255]]
    language_code: Mapped[str] = mapped_column(VARCHAR(10))
    referred_id: Mapped[Optional[user_fk]]
    
    # Association: Access order from User
    orders: Mapped[list["Order"]] = relationship(
        "Order", back_populates="user"
    )

