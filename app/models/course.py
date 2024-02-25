from app.models import Base
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import Session



class Course(Base):
    __tablename__ = 'course'

    course_id = Column(name='id', type_=Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)


    # def save(db: Session)


