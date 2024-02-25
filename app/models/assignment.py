from sqlalchemy import Integer, String, Column, ForeignKey
from app.models import Base



class Assignment(Base):
    __tablename__ = 'assignment'

    assignment_id = Column('id', Integer, primary_key=True, autoincrement=True)
    course_id = Column(Integer, ForeignKey('course.id'), nullable=False)
    assignment_name = Column(String(100), nullable=False)