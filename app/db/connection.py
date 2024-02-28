from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
import configparser



# read sql connection string
parser = configparser.ConfigParser()
parser.read('alembic.ini')
SQL_URL = parser['alembic']['sqlalchemy.url']

# create sql engine
engine = create_engine(SQL_URL)

# session factory
LocalSession = sessionmaker(bind=engine)


# create temp session
def get_db():
    session = LocalSession()
    try:
        yield session
    finally:
        session.close()
