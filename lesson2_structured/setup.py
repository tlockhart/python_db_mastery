from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy import URL
from database.models import Base
from database import orders, products, users, order_products

class DbConfig:
    # def __init__(self, username: str, password: str, host: str, port: int, database: str):
    def __init__(self, username: str, password: str, host: str, port: int, database: str):
        self.username = "postgres"
        self.password = "testpassword"
        self.host = "127.0.0.1"
        self.port = 5432
        self.database = "postgres"
    
    def construct_sqlalchemy_url(self) -> URL:
        return URL.create(
            drivername="postgresql+asyncpg",
            username=self.username,
            password=self.password,
            host=self.host,
            port=self.port,
            database=self.database,
        )

def create_engine(db: DbConfig, echo=False):
    engine = create_async_engine(
        db.construct_sqlalchemy_url(),
        query_cache_size=1200,
        pool_size=20,
        max_overflow=200,
        future=True,
        echo=echo,
    )
    return engine

# One-time setup function to create database schema
async def create_tables(db: DbConfig, echo=False):
    """Create all database tables - run once during setup"""
    engine = create_engine(db, echo=echo)
    
    async with engine.begin() as conn:
        # Create_all: only creates tables that don't already exist
        await conn.run_sync(Base.metadata.create_all)
    
    await engine.dispose()

# Creates session pool to be used by multiple users concurrently
# for ongoing database operations (Max 220)
async def create_session_pool(db: DbConfig, echo=False):
    """Create session pool for runtime database operations"""
    engine = create_engine(db, echo=echo)
    session_pool = async_sessionmaker(bind=engine, expire_on_commit=False)
    return session_pool