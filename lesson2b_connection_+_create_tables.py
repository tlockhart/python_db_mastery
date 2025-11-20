# Step1: Connection String:
from sqlalchemy import create_engine, URL, text, DECIMAL
from sqlalchemy.orm import sessionmaker

# Step2: Table Creation
from datetime import datetime
from typing import Optional, Annotated
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, declared_attr, relationship
from sqlalchemy import BIGINT, TIMESTAMP, VARCHAR, func, ForeignKey, Integer

# Step2: Type Aliases:
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


# Step1: connection string format: driver+postgresql://user:pass@host:port/dbname
##########
url = URL.create(
    drivername="postgresql+psycopg2",
    username="postgres",
    password="testpassword",
    host="127.0.0.1",
    port=5432,
    database="postgres",
)

# echo true for logs
engine = create_engine(url, echo=True)

# Step2: Table creation
########
# USER WITH TYPE ALLIASES:
# Create autoincrement=False so we don't use BIGSERIAL
class User(Base, TimestampMixin, TableNameMixin):
    telegram_id: Mapped[int] = mapped_column(
        BIGINT, primary_key=True, autoincrement=False
    )
    full_name: Mapped[str_255]
    user_name: Mapped[Optional[str_255]]
    language_code: Mapped[str] = mapped_column(VARCHAR(10))
    referred_id: Mapped[Optional[user_fk]]
    
class Product(Base, TimestampMixin, TableNameMixin):
    product_id: Mapped[int_pk]
    title: Mapped[str_255]
    description: Mapped[Optional[str]] = mapped_column(VARCHAR(3000))
    price: Mapped[float] = mapped_column(DECIMAL(precision=16, scale=4))

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



# Use metadata property to create_all tables with using the engine
# Every Table class that inherits from base will be created here
# Create all tables after defining all classes
Base.metadata.create_all(engine)
