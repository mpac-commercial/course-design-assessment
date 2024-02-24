from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy import create_engine
import configparser
from sqlalchemy.orm import DeclarativeBase



class Base(DeclarativeBase):
    pass


parser = configparser.ConfigParser()
parser.read('alembic.ini')
SQL_URL = parser['alembic']['sqlalchemy.url']

engine = create_engine(SQL_URL)

LocalSession = sessionmaker(bind=engine)

# Base.metadata.create_all(bind=engine)
# Base = declarative_base()


def get_db():
    session = LocalSession()
    try:
        yield session
    finally:
        session.close()
