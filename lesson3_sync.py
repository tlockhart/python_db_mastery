import random
import subprocess
import time
import psycopg2
from faker import Faker

from lesson2_structured.database.models.users import User
from lesson2_structured.database.models.orders import Order
from lesson2_structured.database.models.products import Product
from lesson2_structured.database.models.order_products import OrderProduct
from sqlalchemy import and_, func, or_, select
# from sqlalchemy import insert
from sqlalchemy.dialects.postgresql import insert

from lesson2_structured.setup import DbConfig, drop_tables, create_tables, get_session

from sqlalchemy.orm import Session, aliased

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
        stmt = insert(User).values(
                telegram_id=telegram_id,
                full_name=full_name,
                user_name=user_name,
                language_code=language_code,
                referred_id=referred_id
            ).on_conflict_do_update(
                index_elements=[User.telegram_id],
                set_= {
                    "full_name": full_name,
                    "user_name": user_name
                }
            ).returning(
                User
            )
        
        result = self.session.execute(stmt).scalar_one()
        print(f"User: {result.full_name}")
        self.session.commit()
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
                # and_(
                #     User.user_name == "johnny",
                # ),
                or_(
                    User.language_code == "en",
                    User.language_code == "uk",
                    User.language_code == "fr"
                ),
                # User.user_name.ilike("%john%")
            ).order_by(
                User.created_at.desc()
            ).limit(
                10
            )
        #     .group_by(
        #         User.telegram_id
        #    )
            # .having(
            #     User.telegram_id > 0
            # )
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
        
    # Join User and Order tables on User.orders
    def get_all_user_orders(self, telegram_id: int):
        stmt = (
            select(Product, Order, User, OrderProduct)
            .join(User.orders)).join(
                Order.products
            ).join(
                Product
            ).where(
                User.telegram_id == telegram_id
            )
        result = self.session.execute(stmt)
        # Note: Don't use scalars when joining multiple tables with mult labels
        """
        scalars() is designed to extract a single ORM-mapped entity or column 
        from each row of the result. When your SELECT returns multiple entities 
from sqlalchemy import func
        (like Order and User together), each row is a tuple (Order, User), not 
        a single scalar object.
        •	If you call scalars() here, SQLAlchemy will try to treat each row as
            a single object. It gets confused because each row is a tuple, not a
            single mapped instance.
        •	Using .all() returns the full list of tuples, so you can access both
            sides of the join:
        """
        return result.all()
    
    # Count the number of unique orders
    def get_total_number_of_orders(self, telegram_id: int):
        stmt = (
            select(func.count(
                Order.order_id
            )).where(
                Order.user_id == telegram_id
            )
        )
        # shorthand without execute
        result = self.session.scalar(stmt)
        return result
        
        
    # Count the number of orders for all users
    def get_total_number_of_orders_all_users(self):
        stmt = (
            select(func.count(
                Order.order_id
            ).label('quantity'),
                User.full_name
            ).join(
                User
            ).group_by(User.telegram_id)
        )
        # shorthand without execute
        result = self.session.execute(stmt)
        return result
    
    # Sum up the number or products
    def get_total_number_of_products(self):
        stmt = (
            select(func.sum(
                OrderProduct.quantity
            ).label('quantity'),
                User.full_name
            ).join(
                Order,
                Order.order_id == OrderProduct.order_id
            ).join(
                User
            ).group_by(
                User.telegram_id
            ).having(func.sum(OrderProduct.quantity) > 50000)
        )
        # shorthand without execute
        result = self.session.execute(stmt)
        return result
    
    
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
            language_code=random.choice(["en", "uk", "fr"]),
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

    # Inner Joins:
    # get all users who were invited by a referrer (reffered_id)
    def select_all_invited_users(self):
        # Create Alliased Table
        ParentUser = aliased(User)
        ReferralUser = aliased(User)
        
        # Inner Join = Select User who have a reffered_id
        # Full Outer Join Definiton: Returns all users from both tables, wheter or not there is a match on referred_id.
        # To Change stmt to Outer Join use "outerjoin" instead
        stmt = (
            select(ParentUser.full_name.label("parent_name"),
                   ReferralUser.full_name.label("referral_name")
            ).join(
                ReferralUser, ReferralUser.referred_id == ParentUser.telegram_id 
            )
        )
        result = self.session.execute(stmt)
        return result.all()
    
    def select_all_invited_users2(self):
        # Create Alliased Table
        ParentUser = aliased(User)
        ReferralUser = aliased(User)
        
        # Inner Join = Select User who have a reffered_id
        # Full Outer Join Definiton: Returns all users from both tables, wheter or not there is a match on referred_id.
        # To Change stmt to Outer Join use "outerjoin" instead
        stmt = (
            select(ParentUser.full_name.label("parent_name"),
                   ReferralUser.full_name.label("referral_name")
            ).outerjoin(
                ReferralUser, ReferralUser.referred_id == ParentUser.telegram_id 
            ).where(
                ReferralUser.telegram_id.isnot(None),
                ParentUser.referred_id.isnot(None)
            )
        )
        result = self.session.execute(stmt)
        return result.all()
    
def reset_database():
    db = DbConfig()

    # Drop all tables
    print("Dropping all tables...")
    drop_tables(db, echo=True)

    # Recreate tables
    print("Creating tables...")
    create_tables(db, echo=True)

    # Create a session and repo
    Session = get_session(echo=True)
    session = Session()
    repo = Repo(session)

    # Reseed database
    print("Seeding fake data...")
    seed_fake_data(repo)

    print("Database reset and reseeded successfully!")
    

# ----- Main Function -----
def main():
    # Create Session
    Session = get_session()
    session = Session()
    repo = Repo(session)
           
    #################################
    # CALL METHODS HERE:
    #####################
    
    # insert user
    # repo.add_user(
    #     telegram_id=1,
    #     full_name="John Doe",
    #     language_code="en",
    #     user_name="johnny",
    #     referred_id=None
    # )
    
    # get user by id
    # user = repo.get_user_by_id(1)
    # print(f"Full Name: {user.full_name}\n{user}")
    
    # users = repo.get_all_users()
    # for user in users:
    #     print(f"User: {user.telegram_id}: {user.full_name}")
        
    # language = repo.get_user_language(1)
    # print(f"User language: {language}")
    
    # One time data load
    # seed_fake_data(repo)
    
    # Return all users with a referred_id, using inner join
    # Inner Join: Only takes the columns that each table has in common.
    # for row in repo.select_all_invited_users():
    #     print(f"Parent: {row.parent_name}, Referral: {row.referral_name}")
    
    # drop, recreate, and reseed database:
    # reset_database()
    
    # Super Advanced ORM Joins:
    ############################
    # Ineffective: Find the orders a user has created:
    """ 
    Note: Order can reference elements in users, 
    and products through the OrderProducts association
    INEFFECTIVE: Because it doesn't actually join tables
    """
    # for user in repo.get_all_users():
    #     print(f"User: {user.full_name} ({user.telegram_id})")
    #     for order in user.orders:
    #         print(f"  Order ID: {order.order_id}, Created At: {order.created_at}")
    #         for product in order.products:
    #             product = product.product
    #             print(f"    Product: {product.title}, Price: {product.price}")  
    
    # Efficient Approach: Use a join to get the orders and products
    """
    Note: Order can reference elements in users,
    and products through the OrderProducts association
    """
    # user_orders = repo.get_all_user_orders(telegram_id=1418)
    # for row in user_orders:
    #     print(f"#{row.Product.product_id}, Product: {row.Product.title} (x {row.OrderProduct.quantity}), Order ID: {row.Order.order_id}, User: {row.User.full_name}")
    
    # Aggregated Queries: COUNT, SUM, AVG, MIN, MAX
    # Get total number of orders:
    # num_of_orders = repo.get_total_number_of_orders(telegram_id=1418)
    # print(f"Total number of orders: {num_of_orders}")
    
    # Print all user and their number or orders:
    # num_of_orders = repo.get_total_number_of_orders_all_users()
    # for quantity, full_name in num_of_orders:
    #     print(f"Total number of orders: {quantity} by {full_name}")
    
    # Print the sum of all orders:
    sum_of_orders = repo.get_total_number_of_products()
    for quantity, full_name in sum_of_orders:
        print(f"Sum of all products by user: {quantity} by {full_name}")
    
    
# ----- Run everything -----
if __name__ == "__main__":
    start_postgres()
    wait_for_postgres()
    print("Postgres ready, starting DB operations...")
    main()