from datetime import datetime
from typing import Annotated
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, declared_attr
from sqlalchemy import BIGINT, TIMESTAMP, VARCHAR, func, ForeignKey, Integer

class Base(DeclarativeBase):
    pass

# Define a timestamp seperately in a mixin
class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP,
        nullable=False,
        server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP,
        nullable=False,
        server_default=func.now(),
        onupdate=func.now()
    )

# Create mixin to handle tablename 
class TableNameMixin:
    @declared_attr.directive
    def __tablename__(cls) -> str:
        return cls.__name__.lower() + "s"


# Type aliases for reusable column types
int_pk = Annotated[int, mapped_column(Integer, primary_key=True, autoincrement=True)]
user_fk = Annotated[int, mapped_column(BIGINT, ForeignKey('users.telegram_id', ondelete="SET NULL"))]
str_255 = Annotated[str, mapped_column(VARCHAR(255))]