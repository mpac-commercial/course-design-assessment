from sqlalchemy import Integer, Column, ForeignKey
from app.models import Base



class Submission(Base):
    __tablename__ = 'submission'

    submission_id = Column(name='id', type_=Integer, primary_key=True, autoincrement=True)
    course_id = Column('course_id', ForeignKey('course.id'), nullable=False)
    student_id = Column('student_id', ForeignKey('student.id'), nullable=False)
    assignment_id = Column('assignment_id', ForeignKey('assignment.id'), nullable=False)
    grade = Column(type_=Integer, nullable=False)
