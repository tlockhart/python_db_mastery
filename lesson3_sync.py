import random
import subprocess
import time
import psycopg2
from faker import Faker

from lesson2_structured.database.models.users import User
from lesson2_structured.database.models.orders import Order
from lesson2_structured.database.models.products import Product
from lesson2_structured.database.models.order_products import OrderProduct
from sqlalchemy import and_, or_, select
# from sqlalchemy import insert
from sqlalchemy.dialects.postgresql import insert
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

    def add_user(
        self, 
        telegram_id: int, 
        full_name: str, 
        language_code: str, 
        referred_id = None, 
        user_name: str = None) -> User:
        # simple insert
        # stmt = insert(User).values(
        #     telegram_id=telegram_id,
        #     full_name=full_name,
        #     user_name=user_name,
        #     language_code=language_code,
        #     referred_id=referred_id
        # )
        # self.session.execute(stmt)
        # self.session.commit()
        
        # insert if not exists, or update if exists
        stmt = select(User).from_statement(
            insert(User).values(
                telegram_id=telegram_id,
                full_name=full_name,
                user_name=user_name,
                language_code=language_code,
                referred_id=referred_id
            ).returning(
                User
            ).on_conflict_do_update(
                index_elements=[User.telegram_id],
                set_= {
                    "full_name": full_name,
                    "user_name": user_name
                }
            )
        )
        result = self.session.scalars(stmt).first()
        print(f"User: {result.full_name}")
        self.session.execute(stmt)
        return result
        
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
    
    def add_order(self, user_id: int) -> Order:
        stmt = select(Order).from_statement(
            insert(Order).values(
                user_id=user_id
            ).returning(
                Order
            )
        )
        result = self.session.scalars(stmt)
        self.session.commit()
        return result.first()
    
    def add_product(self, title: str, description: str, price: int) -> Product:
        stmt = select(Product).from_statement(
            insert(Product).values(
                title=title,
                description=description,
                price=price
            ).returning(
                Product
            )
        )
        result = self.session.scalars(stmt)
        self.session.commit()
        return result.first()
    
    def add_order_product(self, order_id: int, product_id: int, quantity: int):
        existing = self.session.get(OrderProduct, {"order_id": order_id, "product_id": product_id})
        # Make sure not to make a duplicate record
        if not existing:
            stmt = insert(OrderProduct).values(
                order_id=order_id, 
                product_id=product_id,
                quantity=quantity,
            ).returning(OrderProduct)
            result = self.session.execute(stmt)
            self.session.commit()
            return result.first()
        else:
            # existing.quantity += quantity
            # self.session.commit()
            return existing
        
# Seed the data:
def seed_fake_data(repo: Repo):
    Faker.seed(0)
    # instantiate Faker
    fake = Faker()
    users = []
    orders = []
    products = []
    
    for _ in range(10):
        # Use None for referred_id unless the list has at least one user; 
        # if it does, use the telegram_id of the last user.
        referred_id = None if not users else users[-1].telegram_id
        user = repo.add_user(
            telegram_id=fake.unique.random_int(min=1000, max=9999),
            full_name=fake.name(),
            user_name=fake.user_name(),
            language_code=fake.language_code(),
            referred_id=referred_id
        )
        users.append(user)
        
        # create orders for the user
        for _ in range(10):
            order = repo.add_order(
                user_id=random.choice(users).telegram_id,
            )
            orders.append(order)
            
        # add products
        for _ in range(10):
            product = repo.add_product(
                title=fake.word(),
                description=fake.sentence(),
                price=fake.pyint(),
            )
            products.append(product)
    # add products to orders
    for order in orders:
        for _ in range(3):
            repo.add_order_product(
                order_id=order.order_id,
                product_id=product.product_id,
                quantity=fake.pyint()
            )

# ----- Main Function -----
def main():
    Session = get_session()
    session = Session()
    repo = Repo(session)
    seed_fake_data(repo)

#################################

    # insert user
    repo.add_user(
        telegram_id=1,
        full_name="John Doe",
        language_code="en",
        user_name="johnny",
        referred_id=None
    )
    
    # get user by id
    # user = repo.get_user_by_id(1)
    # print(f"Full Name: {user.full_name}\n{user}")
    
    # users = repo.get_all_users()
    # for user in users:
    #     print(f"User: {user.telegram_id}: {user.full_name}")
        
    language = repo.get_user_language(1)
    print(f"User language: {language}")

# ----- Run everything -----
if __name__ == "__main__":
    start_postgres()
    wait_for_postgres()
    print("Postgres ready, starting DB operations...")
    main()