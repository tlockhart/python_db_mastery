from datetime import datetime
from typing import Optional, Annotated
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, declared_attr, relationship
from sqlalchemy import BIGINT, TIMESTAMP, VARCHAR, func, ForeignKey, Integer


class Base(DeclarativeBase):
    pass


# SIMPLE USER TABLE:
# class User(Base):
#     __tablename__ = "users"
#     # map python type to sqlAlchemy Database types
#     telegram_id: Mapped[int] = mapped_column(BIGINT, primary_key=True)
#     full_name: Mapped[str] = mapped_column(VARCHAR(255), nullable=False)

#     username: Optional[Mapped[str]] = mapped_column(VARCHAR(255), nullable=True)
#     language_code: Mapped[str] = mapped_column(VARCHAR(255), nullable=False)
    
#     created_at: Mapped[datetime] = mapped_column(
#         TIMESTAMP,
#         nullable=False,
#         server_default=func.now()
#     )
#     referred_id: Optional[Mapped[int]] = mapped_column(
#         BIGINT,
#         ForeignKey('users.telegram_id', ondelete="SET NULL"),
#         nullable=True
#     )

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


# USER TABLE WITH MIXINS:
# class User(Base, TimestampMixin, TableNameMixin):
#     # map python type to sqlAlchemy Database types
#     telegram_id: Mapped[int] = mapped_column(BIGINT, primary_key=True)
#     full_name: Mapped[str] = mapped_column(VARCHAR(255), nullable=False)
#     username: Optional[Mapped[str]] = mapped_column(VARCHAR(255), nullable=True)
#     language_code: Mapped[str] = mapped_column(VARCHAR(255), nullable=False)
#     referred_id: Optional[Mapped[int]] = mapped_column(
#         BIGINT,
#         ForeignKey('users.telegram_id', ondelete="SET NULL"),
#         nullable=True
#     )


# Type aliases for reusable column types
int_pk = Annotated[int, mapped_column(Integer, primary_key=True, autoincrement=True)]
user_fk = Annotated[int, mapped_column(BIGINT, ForeignKey('users.telegram_id', ondelete="SET NULL"))]
str_255 = Annotated[str, mapped_column(VARCHAR(255))]

# USER WITH TYPE ALLIASES:
class User(Base, TimestampMixin, TableNameMixin):
    telegram_id: Mapped[int] = mapped_column(
        BIGINT, primary_key=True,
    )
    full_name: Mapped[str_255]
    username: Optional[Mapped[str_255]]
    language_code: Mapped[str_255]
    referred_id: Optional[Mapped[user_fk]]
    
class Product(Base, TimestampMixin, TableNameMixin):
    product_id: Mapped[int_pk]
    title: Mapped[str_255]
    description: Optional[Mapped[str]]

class Order(Base, TimestampMixin, TableNameMixin):
    order_id: Mapped[int_pk]
    user_id: Mapped[user_fk]

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
    # order = relationship("Order", back_populates="order_products")
    
# user = User()
# user.full_name = "Alice"
