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


app = FastAPI()


course_service = CourseServiceImpl()


@app.get('/course/all/', response_model=AllCourseView)
def get_all_courses():
  # fetch course list
  all_courses = course_service.get_courses()
  # check if any course record exists
  if not all_courses:
    raise HTTPException(status_code=404, detail={
      'description': 'Item not found.',
      'message': 'No courses was found!'
    })
  return {
    'count_course': len(all_courses),
    'course_list': [CourseView.model_validate(course_instance).model_dump() for course_instance in all_courses]
  }


@app.get(path='/course/{course_id}/', response_model=CourseView)
def get_course(course_id: int):
  # fetch course frim database
  db_course = course_service.get_course_by_id(course_id)
  # Check for existance of course
  if db_course is None:
    raise HTTPException(status_code=404, detail={
      'description': 'Item not found.',
      'message': f'course not found with ID {course_id}!'
    })
  return db_course


@app.post(path="/course/create/", response_model=CourseView)
def create_course(request: CourseCreate):
  db_course = course_service.create_course(request.course_name)
  return db_course


@app.delete(path="/course/delete/{course_id}", response_model=CourseView)
def delete_course_by_id(course_id: int):
  db_course = course_service.delete_course(course_id=course_id)
  return db_course


@app.post(path='/assignment/create/', response_model=AssignmentView)
def create_assignment(request: AssignmentCreate):
  # fetch course from database
  db_course = course_service.get_course_by_id(request.course_id)\
  # check if course exists
  if db_course is None:
    raise HTTPException(status_code=404, detail={
      'desccription': 'cannot create assignment.',
      'message': f'Course not found with ID {request.course_id}'
    })

  # crate assignment schema from database
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
def enroll_student(request: StudentCourseCreate):
  # fetch student from database
  db_student = course_service.get_student_by_id(request.student_id)
  # check if student exists
  if db_student is None:
    raise HTTPException(status_code=404, detail={
      'description': 'cannot enroll student.',
      'message': f'could not find student with ID {request.student_id}'
    })
  # create student schema from database
  student_instance = StudentView(
    student_name=db_student.student_name,
    student_id=db_student.student_id
    )

  # fetch course from database
  db_course = course_service.get_course_by_id(db_student_course.course_id)
  # check if course exists
  if db_course is None:
    raise HTTPException(status_code=404, detail={
      'description': 'cannot enroll student',
      'message': f'could not find course with ID {request.course_id}'
    })
  # create course schema from database
  course_instance = CourseView(
    course_id=db_course.course_id,
    course_name=db_course.course_name
  )
  
  # create student-course schema from database
  db_student_course = course_service.enroll_student(
    course_id=request.course_id,
    student_id=request.student_id
  )

  return StudentCourseView(
    student_course_id=db_student_course.student_course_id,
    course_instance=course_instance, 
    student_instance=student_instance
    )

@app.delete(path='/student/dropout/', response_model=StudentCourseView)
def dropout_student(request: StudentCourseCreate):
  db_student = course_service.get_student_by_id(request.student_id)
  # check if the student with student_id exists
  if db_student is None:
    raise HTTPException(status_code=404, detail={
      'description': 'cannot dropout student.',
      'message': f'student with ID {request.student_id} was not found!'
    })
  student_instance = StudentView.model_validate(db_student)

  db_course = course_service.get_course_by_id(request.course_id)
  # check if course with course_id exists
  if db_course is None:
    raise HTTPException(status_code=404, detail={
      'description': 'cannot dropout student.',
      'message': f'course with ID {request.course_id} was not found!'
    })
  course_instance = CourseView.model_validate(db_course)

  # dropout student
  deleted_student_course = course_service.dropout_student(
    student_id=request.student_id,
    course_id=request.course_id
  )

  return {
    'student_course_id': deleted_student_course.student_course_id,
    'student_instance': student_instance.model_dump(),
    'course_instance': course_instance.model_dump( )
  }

@app.post(path='/submission/create/', response_model=SubmissionView)
def create_submission(request: SubmissionCreate):
  
  db_course = course_service.get_course_by_id(course_id=request.course_id)
  #check if course exists
  if db_course is None:
    raise HTTPException(status_code=404, detail={
      'description': 'cannot create submission.',
      'message': f'could not find course with ID {request.course_id}'
    })

  db_student = course_service.get_student_by_id(student_id=request.student_id)
  # check if student exitst
  if db_student is None:
    raise HTTPException(status_code=404, detail={
      'description': 'cannot create submission',
      'message': f'could not find student with ID {request.student_id}'
    })
  
  db_assignment = course_service.get_assignment_by_id(assignment_id=request.assignment_id)
  # check if assignment exists
  if db_assignment is None:
    raise HTTPException(status_code=404, detail={
      'description': 'cannot create submission.',
      'message': f'could not found assignment with ID {request.assignment_id}'
    })

  # check if request course_id and assignment course_id match
  if db_assignment.course_id != request.course_id:
    raise HTTPException(status_code=409, detail={
      'description': 'cannot create submission.',
      'message': f"course ID with ID {request.course_id} is not matched with assignment's course ID {db_assignment.course_id}."
    })

  # add submission to database
  db_submission = course_service.submit_assignment(
    course_id=request.course_id,
    student_id=request.student_id,
    assignment_id=request.assignment_id,
    grade=request.grade
  )

  # create schemas from database
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
  # check if course exists
  if db_course is None:
    raise HTTPException(status_code=404, detail={
      'description': 'request cannot be made.',
      'message': f'no course was found with ID {request.course_id}'
    })
  #create course schema from database
  course_instance = CourseView.model_validate(db_course)

  db_student = course_service.get_student_by_id(request.course_id)
  # check if student exists
  if db_student is None:
    raise HTTPException(status_code=404, detail={
      'description': 'request cannot be made.',
      'message': f'no student was found with ID {request.student_id}'
    })
  # create student schema from database
  student_instance = StudentView.model_validate(db_student)

  grade = course_service.get_student_grade_avg(course_id=request.course_id, student_id=request.student_id)

  return {
    'course_instance': course_instance,
    'student_instance': student_instance,
    'grade': grade
  }


@app.get('/submission/average-course-assignment/', response_model=SubmissionAvgCourseAssignment)
def get_average_course_assignment(request: CourseAssignment):
  # fetch course instance by course_id
  db_course = course_service.get_course_by_id(request.course_id)
  # check if course exists
  if db_course is None:
    raise HTTPException(status_code=404, detail={
      'description': 'request cannot be made.',
      'message': f'could not find course with ID {request.course_id}'
    })  
  # create course schema from database
  course_instance = CourseView.model_validate(db_course)
  
  # fetch assignment by assignment_id
  db_assignment = course_service.get_assignment_by_id(assignment_id=request.assignment_id)
  # check if assignment exists
  if db_assignment is None:
    raise HTTPException(status_code=404, detail={
      'description': 'request could not be made',
      'message': f'could not find assignment with ID {request.assignment_id}'
    })

  # check if user prompted course_id matches the assignemnt course_id
  if db_assignment.course_id != request.course_id:  
    raise HTTPException(status_code=409, detail={
      'description': 'request could not be made',
      'message': f'course with ID {request.course_id} does not match the assignment\'s course with ID {db_assignment.course_id}'
    })

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
  # check if course exists
  if db_course is None:
    raise HTTPException(status_code=404, detail={
      'description': 'request cannot be made',
      'message': f'could not find course with ID {course_id}'
    })
  
  top_students = course_service.get_top_five_students(course_id=course_id)
  return {
    'course_instance': CourseView.model_validate(db_course).model_dump(),
    'students': top_students
  }  


if __name__ == "__main__":
  uvicorn.run(app, host='127.0.0.1', port=8080)

  
