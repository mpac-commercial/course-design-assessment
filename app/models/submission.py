from sqlalchemy import Integer, Column, ForeignKey
from app.models import course, student, assignment
from app.db.connection import Base



class Submission(Base):
    __tablename__ = 'Submission'

    submission_id = Column(name='id', type_=Integer, primary_key=True, autoincrement=True)
    course_id = Column('course_id', ForeignKey(course.Course.course_id), nullable=False)
    student_id = Column('student_id', ForeignKey(student.Student.student_id), nullable=False)
    assignment_id = Column('assignment_id', ForeignKey(assignment.Assignment.assignment_id), nullable=False)
    grade = Column(type_=Integer, nullable=False)
