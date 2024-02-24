from sqlalchemy import Integer, String, Column, ForeignKey
from app.db.connection import Base
from .course import Course



class Assignment(Base):
    __tablename__ = 'Assignment'

    id = Column(Integer, primary_key=True, autoincrement=True)
    course_id = Column(Integer, ForeignKey(Course.id), nullable=False)
    name = Column(String, nullable=False)
