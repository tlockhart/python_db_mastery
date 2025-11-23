import subprocess
import time
import psycopg2
from lesson2_structured.database.models.users import User
from sqlalchemy import and_, insert, or_, select
from lesson2_structured.setup import get_session
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

    def add_user(self, telegram_id: int, full_name: str, language_code: str, referrer_id = None, user_name: str = None):
        stmt = insert(User).values(
            telegram_id=telegram_id,
            full_name=full_name,
            user_name=user_name,
            language_code=language_code,
            referrer_id=referrer_id
        )
        self.session.execute(stmt)
        self.session.commit()
        
    def get_user_by_id(self, telegram_id: int) -> User | None:
        stmt = select(User).where(User.telegram_id == telegram_id)
        result = self.session.execute(stmt)
        # user = result.scalar_one_or_none()
        # return the actual values not the tuple
        return result.scalars().first()
    
    def get_all_users(self) -> list[User]:
        stmt = select(
            User
            ).where(
                and_(
                    User.user_name == "johnny",
                ),
                or_(
                    User.language_code == "en",
                    User.language_code == "uk"
                ),
                User.user_name.ilike("%john%")
            ).group_by(
                User.telegram_id
           ).order_by(
                User.created_at.desc()
            ).limit(
                10
            ).having(
                User.telegram_id > 0
            )
        result = self.session.execute(stmt) 
        # return the actual values not the tuple
        return result.scalars().all()
    
    def get_user_language(self, telegram_id: int) -> str:
        stmt = select(User.language_code).where(User.telegram_id == telegram_id).order_by(
            User.created_at.desc()
        )
        result = self.session.execute(stmt)
        # select one column of one row
        return result.scalars().first()

# ----- Main Function -----
def main():
    Session = get_session()
    session = Session()
    repo = Repo(session)

    # insert user
    # repo.add_user(
    #     telegram_id=1,
    #     full_name="John Doe",
    #     language_code="en",
    #     user_name="johnny",
    #     referrer_id=None
    # )
    
    # get user by id
    # user = repo.get_user_by_id(1)
    # print(f"Full Name: {user.full_name}\n{user}")
    
    users = repo.get_all_users()
    for user in users:
        print(f"User: {user.telegram_id}: {user.full_name}")
        
    language = repo.get_user_language(1)
    print(f"User language: {language}")
    



# ----- Run everything -----
if __name__ == "__main__":
    start_postgres()
    wait_for_postgres()
    print("Postgres ready, starting DB operations...")
    main()