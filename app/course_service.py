from abc import ABC, abstractmethod
from typing import List, Any


class CourseService(ABC):
    @abstractmethod
    def get_courses(self) -> List[Any]:
        """
        Returns a list of all courses.
        """
        pass

    @abstractmethod
    def get_course_by_id(self, course_id) -> Any:
        """
        Returns a course by its id.
        """
        pass

    @abstractmethod
    def create_course(self, course_name) -> int:
        """
        Creates a new course.
        Returns the id of the new course.
        """
        pass

    @abstractmethod
    def delete_course(self, course_id) -> bool:
        """
        Deletes a course by its id.
        Returns True if the course was deleted successfully, otherwise False.
        """
        pass

    @abstractmethod
    def create_assignment(self, course_id, assignment_name) -> int:
        """
        Creates a new assignment for a course.
        Returns the id of the new assignment.
        """
        pass

    @abstractmethod
    def enroll_student(self, course_id, student_id) -> bool:
        """
        Enrolls a student in a course.
        Returns True if the student was enrolled successfully, otherwise False.
        """
        pass

    @abstractmethod
    def dropout_student(self, course_id, student_id) -> bool:
        """
        Drops a student from a course.
        Returns True if the student was dropped successfully, otherwise False.
        """
        pass

    @abstractmethod
    def submit_assignment(self, course_id, student_id, assignment_id, grade: int) -> bool:
        """
        Submits an assignment for a student. A grade of an assignment will be an integer between 0 and 100 inclusive.
        Returns True if the assignment was submitted successfully, otherwise False.
        """
        pass

    @abstractmethod
    def get_assignment_grade_avg(self, course_id, assignment_id) -> int:
        """
        Returns the average grade for an assignment. Floors the result to the nearest integer.
        """
        pass

    @abstractmethod
    def get_student_grade_avg(self, course_id, student_id) -> int:
        """
        Returns the average grade for a student in a course. Floors the result to the nearest integer.
        """
        pass

    @abstractmethod
    def get_top_five_students(self, course_id) -> List[int]:
        """
        Returns the IDs of the top 5 students in a course based on their average grades of all assignments.
        """
        pass
