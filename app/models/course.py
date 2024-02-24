from app.models import Base
from sqlalchemy import Column, Integer, String



class Course(Base):
    __tablename__ = 'course'

    course_id = Column(name='id', type_=Integer, primary_key=True, autoincrement=True)
    course_name = Column(String(100), nullable=False)



