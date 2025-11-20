## virtual environment: pip install virtualenv
## python -m virtualenv venv
## activaute venv: source venv/bin/activate
## pip install psycopg2-binary
## pip install asyncpg sqlalchemy~=2.0

## create a docker container with our database: 
## uses default user and postgres database: postgres
## postgres/testpassword/postgres/127.0.0.1
## docker run --name postgresql -e POSTGRES_PASSWORD=testpassword -p 5432:5432 -d postgres:13

## remove postgresql

## section 1: https://gist.github.com/Latand/8b2266417ad0cef9c384768a6dc8ba1c
## Section 2: https://gist.github.com/Latand/5eda75a319dd4b35639a8bb9c11e0b89
## section 3: https://gist.github.com/Latand/6c10e09d5d4582095d4ebe2e0d113578

## Start Docker:
docker start postgresql

## Check if container is running:
docker ps

## Create docker daemon
"""docker rm -f postgresql && docker run --name postgresql -e POSTGRES_PASSWORD=testpassword -p 5432:5432 -d postgres:13
"""
##

User: postgres (default)
Password: testpassword
Database: postgres (default)
Host: 127.0.0.1

## Create an requirement.txt file with dependencies:
### source venv/bin/activate && pip freeze > requirements.txt

## Create alembic migrations folder:
### python -m alembic init alembic

## Add git ignore file:
git init

## Step1: Run alembic migration for initial changes
### alembic revision --autogenerate -m "initial migration"

## Step2: Apply existing migration
### alembic upgrade head

## Step3: New migration:
### alembic revision --autogenerate -m "second migration"

## Step4: Apply existing migration
### alembic upgrade head, apply all migrations
### alembic downgrade +1, Applay all migrations
### alembic downgrade -1, Go back to previous

## Step 4 _optional: Reset Alembic state:
# Delete the existing migration file
### rm alembic/versions/b0fe2efd5628_initial_migration.py

# Create a fresh migration
### alembic revision --autogenerate -m "initial migration"


# Import syntax: from package(directory) import module (file)
# Or             from package.file import class1, class2..