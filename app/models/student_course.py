from sqlalchemy import Column, ForeignKey, Integer
from app.db.connection import Base




class StudentCourse(Base):
    __tablename__ = 'Student_Course'

    student_course_id = Column('id', Integer, primary_key=True, autoincrement=True)
    course_id = Column('course_id', ForeignKey('Course.id'))
    student_id = Column('student_id', ForeignKey('Student.id'))

