from app.db.connection import Base
from sqlalchemy import Column, Integer, String



class Course(Base):
    __tablename__ = 'Course'

    id = Column(Integer, primary_key=True, autoincrement=True)
    course_name = Column(String(100), nullable=False)


