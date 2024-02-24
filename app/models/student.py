from sqlalchemy import Integer, String, Column
from app.db.connection import Base



class Student(Base):
    __tablename__ = 'Student'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False)

