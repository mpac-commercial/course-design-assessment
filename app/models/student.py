from sqlalchemy import Integer, String, Column
from app.db.connection import Base



class Student(Base):
    __tablename__ = 'Student'

    student_id = Column(name='id', type_=Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False)

