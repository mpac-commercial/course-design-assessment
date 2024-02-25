from sqlalchemy import Column, ForeignKey, Integer
from app.models import Base




class StudentCourse(Base):
    __tablename__ = 'student_course'

    student_course_id = Column('id', Integer, autoincrement=True, primary_key=True)
    course_id = Column('course_id', ForeignKey('course.id'), nullable=False, index=True)
    student_id = Column('student_id', ForeignKey('student.id'), nullable=False, index=True)

