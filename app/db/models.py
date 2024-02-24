from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, ForeignKey, String, Integer

Base = declarative_base()


class Course(Base):
    __tablename__ = 'course'

    course_id = Column('id', Integer, primary_key=True, autoincrement=True)
    name = Column('name', String(100), nullable=False)



class Student(Base):
    __tablename__ = 'student'

    student_id = Column('id', Integer, primary_key=True, autoincrement=True)
    name = Column('name', String(50), nullable=False)



class Assignment(Base):
    __tablename__ = 'assignment'

    assignment_id = Column('id', Integer, primary_key=True, autoincrement=True)
    course_id = Column('course_id', Integer, ForeignKey(Course.course_id), nullable=False)
    name = Column('name', String(100), nullable=False)


class Submission(Base):
    __tablename__ = 'submission'

    submission_id = Column('id', Integer, primary_key=True, autoincrement=True)
    course_id = Column('course_id', ForeignKey(Course.course_id), nullable=False)
    student_id = Column('student_id', ForeignKey(Student.student_id), nullable=False)
    assignment_id = Column('assignment_id', ForeignKey(Assignment.assignment_id), nullable=False)
    grade = Column('grade', Integer, nullable=False)


class StudentCourse(Base):
    __tablename__ = 'Student_Course'

    student_course_id = Column('id', Integer, primary_key=True, autoincrement=True)
    course_id = Column('course_id', ForeignKey(Course.course_id))
    student_id = Column('student_id', ForeignKey(Student.student_id))