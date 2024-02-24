from app.db.connection import Base
from sqlalchemy import Column, Integer, String



class Course(Base):
    __tablename__ = 'Course'

    course_id = Column(name='id', type_=Integer, primary_key=True, autoincrement=True)
    course_name = Column(String(100), nullable=False)



