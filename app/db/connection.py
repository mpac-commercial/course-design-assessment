from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy import create_engine
import configparser
from sqlalchemy.orm import DeclarativeBase



parser = configparser.ConfigParser()
parser.read('alembic.ini')
SQL_URL = parser['alembic']['sqlalchemy.url']

engine = create_engine(SQL_URL)

LocalSession = sessionmaker(bind=engine)

# Base = declarative_base()
# Base.metadata.create_all(bind=engine)


def get_db():
    session = LocalSession()
    try:
        yield session
    finally:
        session.close()
