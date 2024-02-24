from sqlalchemy import Integer, String, Column, ForeignKey
from app.db.connection import Base
from .course import Course



class Assignment(Base):
    __tablename__ = 'Assignment'

    assignment_id = Column(name='assignment', type_=Integer, primary_key=True, autoincrement=True)
    course_id = Column(Integer, ForeignKey(Course.course_id), nullable=False)
    name = Column(String(100), nullable=False)
