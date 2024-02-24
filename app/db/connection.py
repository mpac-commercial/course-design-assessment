from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
import configparser




parser = configparser.ConfigParser()
parser.read('alembic.ini')
SQL_URL = parser['alembic']['sqlalchemy.url']

engine = create_engine(SQL_URL)

LocalSession = sessionmaker(bind=engine)


def get_db():
    session = LocalSession()
    try:
        yield session
    finally:
        session.close()
