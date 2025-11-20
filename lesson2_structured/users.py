# Step2: Table Creation
from typing import Optional
from sqlalchemy.orm import Mapped, mapped_column, VARCHAR
from sqlalchemy import BIGINT

from lesson2_structured.database.models.base import Base, TimestampMixin, TableNameMixin, str_255, user_fk


# USER WITH TYPE ALLIASES:
class User(Base, TimestampMixin, TableNameMixin):
    telegram_id: Mapped[int] = mapped_column(
        BIGINT, primary_key=True, autoincrement=False
    )
    full_name: Mapped[str_255]
    user_name: Mapped[Optional[str_255]]
    language_code: Mapped[str] = mapped_column(VARCHAR(10))
    referred_id: Mapped[Optional[user_fk]]

