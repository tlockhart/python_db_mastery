## virtual environment: pip install virtualenv
## python -m virtualenv venv
## activaute venv: source venv/bin/activate
## pip install psycopg2-binary
## pip install asyncpg sqlalchemy~=2.0
## create a docker container with our database: 
## docker run --name postgresql -e POSTGRES_PASSWORD=testpassword -e POSTGRES_USER=testuser -e POSTGRES_DB=testuser -p 5432:5432 -d postgres:13.4-alpine

## remove postgresql

## section 1: https://gist.github.com/Latand/8b2266417ad0cef9c384768a6dc8ba1c
## Section 2: https://gist.github.com/Latand/5eda75a319dd4b35639a8bb9c11e0b89