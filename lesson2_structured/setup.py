# setup_sync.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import URL
from .database.models.base import Base
from environs import Env

env = Env()
env.read_env('.env')

class DbConfig:
    def __init__(self):
        self.username = env.str("POSTGRES_USER")
        self.password = env.str("POSTGRES_PASSWORD")
        self.host = env.str("DATABASE_HOST")
        self.port = 5432
        self.database = env.str("POSTGRES_DB")

    def construct_sqlalchemy_url(self) -> URL:
        # Use sychronous driver
        return URL.create(
            drivername="postgresql+psycopg2",
            username=self.username,
            password=self.password,
            host=self.host,
            port=self.port,
            database=self.database,
        )

def create_engine_sync(db: DbConfig, echo=False):
    return create_engine(
        db.construct_sqlalchemy_url(), 
        echo=echo,
        pool_size=200,       # number of persistent connections
        max_overflow=0,      # extra connections beyond pool_size
        pool_pre_ping=True   # check connections are alive
    )

def create_tables(db: DbConfig, echo=False):
    engine = create_engine_sync(db, echo=echo)
    Base.metadata.create_all(engine)
    engine.dispose()

def get_session(echo=False):
    db = DbConfig()
    engine = create_engine_sync(db, echo=echo)
    Session = sessionmaker(bind=engine, expire_on_commit=False)
    return Session