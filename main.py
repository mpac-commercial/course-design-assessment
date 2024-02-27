from app.services.course_service_impl import CourseServiceImpl
from fastapi import FastAPI, HTTPException
from app.schemas.course import CourseView, CourseCreate, AllCourseView
from app.schemas.assignment import AssignmentCreate, AssignmentView
from app.schemas.student import StudentView
from app.schemas.student_course import StudentCourseView, StudentCourseCreate
from app.schemas.submission import (
  SubmissionCreate,
  SubmissionView, 
  SubmissionAvgCourseAssignment, 
  SubmissionAvgCourseStudent, 
  CourseAssignment,
  SubmissionTopCourseGrades
)
import uvicorn
import json
from typing import List



if __name__ == "__main__":
  course_service = CourseServiceImpl()

  app = FastAPI()
  

  @app.get('/course/all/', response_model=AllCourseView)
  def get_all_courses():
    all_courses = course_service.get_courses()
    if not all_courses:
      raise HTTPException(status_code=404, detail={
        'description': 'Item not found.',
        'message': 'No courses was found!'
      })
    return {
      'count_course': len(all_courses),
      'course_list': [CourseView.model_validate(course_instance).model_dump() for course_instance in all_courses]
    }

  @app.get(path='/course/{course_id}', response_model=CourseView)
  def get_course(course_id: int):
    db_course = course_service.get_course_by_id(course_id)
    # Check for existance of course
    if db_course is None:
      raise HTTPException(status_code=404, detail={
        'description': 'Item not found.',
        'message': f'course not found with ID {course_id}!'
      })
    return db_course
  

  @app.post(path="/course/create/", response_model=CourseView)
  def create_course(course_schema: CourseCreate):
    db_course = course_service.create_course(course_schema.course_name)
    return db_course
  

  @app.delete(path="/course/delete/{course_id}", response_model=CourseView)
  def delete_course_by_id(course_id: int):
    db_course = course_service.delete_course(course_id=course_id)
    return db_course


  @app.post(path='/assignment/create/', response_model=AssignmentView)
  def create_assignment(request: AssignmentCreate):
    db_course = course_service.get_course_by_id(request.course_id)
    if db_course is None:
      raise HTTPException(status_code=404, detail={
        'desccription': 'cannot create assignment.',
        'message': f'Course not found with ID {request.course_id}'
      })

    db_assignment = course_service.create_assignment(
      course_id=request.course_id,
      assignment_name=request.assignment_name
    )

    return AssignmentView(
      assignment_id=db_assignment.assignment_id,
      course_instance={'course_id':db_course.course_id, 'course_name': db_course.course_name},
      assignment_name=db_assignment.assignment_name
    )
  
  
  @app.post(path='/student/enroll/', response_model=StudentCourseView)
  def enroll_student(student_course_schema: StudentCourseCreate):
    db_student_course = course_service.enroll_student(
      course_id=student_course_schema.course_id,
      student_id=student_course_schema.student_id
    )

    db_student = course_service.get_student_by_id(student_course_schema.student_id)
    student_instance = StudentView(
      student_name=db_student.student_name,
      student_id=db_student.student_id
      )

    db_course = course_service.get_course_by_id(db_student_course.course_id)
    course_instance = CourseView(
      course_id=db_course.course_id,
      course_name=db_course.course_name
    )

    return StudentCourseView(
      student_course_id=db_student_course.student_course_id,
      course_instance=course_instance, 
      student_instance=student_instance
      )

  @app.delete(path='/student/dropout/', response_model=StudentCourseView)
  def dropout_student(student_course_schema: StudentCourseCreate):
    db_student = course_service.get_student_by_id(deleted_student_course.student_id)
    if db_student is None:
      raise HTTPException(status_code=404, detail={
        'description': 'cannot dropout student.',
        'message': f'student with ID {student_course_schema.student_id} was not found!'
      })
    student_instance = StudentView.model_validate(db_student)

    db_course = course_service.get_course_by_id(deleted_student_course.course_id)
    course_instance = CourseView.model_validate(db_course)

    deleted_student_course = course_service.dropout_student(
      student_id=student_course_schema.student_id,
      course_id=student_course_schema.course_id
    )

    return {
      'student_course_id': deleted_student_course.student_course_id,
      'student_instance': student_instance.model_dump(),
      'course_instance': course_instance.model_dump( )
    }

  @app.post(path='/submission/', response_model=SubmissionView)
  def create_submission(submission_schema: SubmissionCreate):
    db_assignment = course_service.get_assignment_by_id(assignment_id=submission_schema.assignment_id)
    if db_assignment is None:
      pass

    if db_assignment.course_id != submission_schema.course_id:
      pass

    db_course = course_service.get_course_by_id(course_id=submission_schema.course_id)
    if db_course is None:
      pass

    db_student = course_service.get_student_by_id(student_id=submission_schema.student_id)
    if db_student is None:
      pass

    db_submission = course_service.submit_assignment(
      course_id=submission_schema.course_id,
      student_id=submission_schema.student_id,
      assignment_id=submission_schema.assignment_id,
      grade=submission_schema.grade
    )

    course_instance = CourseView.model_validate(db_course)
    student_instance = StudentView.model_validate(db_student)

    return {
      'submission_id': db_submission.submission_id,
      'course_instance': course_instance,
      'student_instance': student_instance,
      'assignment_instance': AssignmentView.model_validate_json(json.dumps({
        'assignment_id': db_assignment.assignment_id,
        'course_instance': course_instance.model_dump(),
        'assignment_name': db_assignment.assignment_name
      })),
      'grade': db_submission.grade
    }
  

  @app.get('/submission/average-course-student/', response_model=SubmissionAvgCourseStudent)
  def get_average_course_student(request: StudentCourseCreate):
    db_course = course_service.get_course_by_id(request.course_id)
    if db_course is None:
      pass
    course_instance = CourseView.model_validate(db_course)

    db_student = course_service.get_student_by_id(request.student_id)
    if db_student is None:
      pass
    student_instance = StudentView.model_validate(db_student)

    grade = course_service.get_student_grade_avg(course_id=request.course_id, student_id=request.student_id)

    return {
      'course_instance': course_instance,
      'student_instance': student_instance,
      'grade': grade
    }
  

  @app.get('/submission/average-course-assignment/', response_model=SubmissionAvgCourseAssignment)
  def get_average_course_assignment(request: CourseAssignment):
    db_assignment = course_service.get_assignment_by_id(assignment_id=request.assignment_id)
    if db_assignment is None:
      pass

    if db_assignment.course_id != request.course_id:
      pass

    db_course = db_course = course_service.get_course_by_id(request.course_id)
    if db_course is None:
      pass
    course_instance = CourseView.model_validate(db_course)

    grade = course_service.get_assignment_grade_avg(course_id=request.course_id, assignment_id=request.assignment_id)
    return {
      'course_instance': course_instance,
      'assignment_instance': AssignmentView.model_validate_json(json.dumps({
        'assignment_id': db_assignment.assignment_id,
        'assignment_name': db_assignment.assignment_name,
        'course_instance': course_instance.model_dump()
      })),
      'grade': grade
    }


  @app.get('/submission/{course_id}/top5/', response_model=SubmissionTopCourseGrades)
  def get_top_course_students(course_id: int):
    db_course = course_service.get_course_by_id(course_id=course_id)
    if db_course is None:
      pass
    
    top_students = course_service.get_top_five_students(course_id=course_id)
    return {
      'course_instance': CourseView.model_validate(db_course).model_dump(),
      'students': top_students
    }  



  uvicorn.run(app, host='127.0.0.1', port=8080)

  
