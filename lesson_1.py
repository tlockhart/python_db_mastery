from sqlalchemy import create_engine, URL, text
from sqlalchemy.orm import sessionmaker

# connection string format: driver+postgresql://user:pass@host:port/dbname
url = URL.create(
    drivername="postgresql+psycopg2",
    username="testuser",
    password="testpassword",
    host="localhost",
    port=5432,
    database="testuser",
)

# echo true for logs
engine = create_engine(url, echo=True)

# we need a session pool to connect mult (people)session to our db at a time
# Their is a softlayer of connection that will be used as needed, or overhead connection of 200 that are destroyed when completed
session_pool = sessionmaker(engine)

# session = session_pool()
# session.execute()
# session.commit()
# session.close()

# Create table
with session_pool() as session:
    create_table_query = text("""
    CREATE TABLE IF NOT EXISTS users (
        telegram_id     BIGINT PRIMARY KEY,
        full_name       VARCHAR(255) NOT NULL,
        username        VARCHAR(255),
        language_code   VARCHAR(255) NOT NULL,
        created_at      TIMESTAMP DEFAULT NOW(),
        referrer_id     BIGINT,
        FOREIGN KEY (referrer_id)
            REFERENCES users (telegram_id)
            ON DELETE SET NULL
    );
    """)
    session.execute(create_table_query)
    session.commit()

# Clear existing data and insert new data
with session_pool() as session:
    # Clear existing data
    delete_query = text("DELETE FROM users;")
    session.execute(delete_query)
    
    # Insert new data
    insert_query = text("""
    INSERT INTO users (telegram_id, full_name, username, language_code, referrer_id)
    VALUES (1, 'John Doe', 'johndoe', 'en', NULL),
           (2, 'Jane Doe', 'janedoe', 'en', 1);
    """)
    session.execute(insert_query)
    session.commit()

# Select data
with session_pool() as session:
    select_query = text("""
    SELECT * FROM users;
    """)
    results = session.execute(select_query)
    print(f"{results}")
    
    # row1 = results.first()
    # print(f"row1: {row1}")
    
    
    # for row in results:
    #     print(row.full_name)
    rows = results.all()
    print(f"rows: {rows}")
   
