from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy import create_engine
import configparser



Base = declarative_base()

parser = configparser.ConfigParser()
parser.read('alembic.ini')
SQL_URL = parser['alembic']['sqlalchemy.url']

engine = create_engine(SQL_URL)

LocalSession = sessionmaker(bind=engine)

# Base.metadata.create_all(bind=engine)


def get_db():
    session = LocalSession()
    try:
        yield session
    finally:
        session.close()
