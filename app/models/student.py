from sqlalchemy import Integer, String, Column
from app.models import Base



class Student(Base):
    __tablename__ = 'student'

    student_id = Column(name='id', type_=Integer, primary_key=True, autoincrement=True)
    student_name = Column(String(50), nullable=False)

