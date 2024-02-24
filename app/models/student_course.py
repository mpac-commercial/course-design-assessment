from sqlalchemy import Column, ForeignKey, Integer
from app.models import Base




class StudentCourse(Base):
    __tablename__ = 'student_course'

    student_course_id = Column('id', Integer, primary_key=True, autoincrement=True)
    course_id = Column('course_id', ForeignKey('course.id'))
    student_id = Column('student_id', ForeignKey('student.id'))

