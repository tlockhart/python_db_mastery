import subprocess
import time
import psycopg2
import asyncio
from lesson2_structured.database.models.users import User
from sqlalchemy import insert
from lesson2_structured.setup_async import get_session
from sqlalchemy.orm import Session

# ----- Docker/Postgres Startup -----
def start_postgres():
    subprocess.run(["docker-compose", "up", "-d"], check=True)

def wait_for_postgres():
    while True:
        try:
            conn = psycopg2.connect(
                host="127.0.0.1",
                database="postgres",
                user="postgres",
                password="testpassword"
            )
            conn.close()
            break
        except psycopg2.OperationalError:
            print("Waiting for Postgres to start...")
            time.sleep(2)

# ----- Repo Class -----
class Repo:
    def __init__(self, session: Session):
        self.session = session

    async def add_user(
        self, 
        telegram_id: int, 
        full_name: str, 
        language_code: str, 
        user_name: str = None,
        referrer_id=None
    ):
        stmt = insert(User).values(
            telegram_id=telegram_id,
            full_name=full_name,
            user_name=user_name,
            language_code=language_code,
            referrer_id=referrer_id
        )
        await self.session.execute(stmt)
        await self.session.commit()

# ----- Main Async Function -----
async def main():
    session_pool = await get_session()
    async with session_pool() as session:
        repo = Repo(session)
        await repo.add_user(
            telegram_id=1,
            full_name="John Doe",
            language_code="en",
            user_name="johnny"
        )

# ----- Run everything -----
if __name__ == "__main__":
    start_postgres()
    wait_for_postgres()
    print("Postgres ready, starting async DB operations...")
    asyncio.run(main())