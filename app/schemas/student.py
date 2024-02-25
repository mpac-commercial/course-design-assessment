from pydantic import BaseModel
from app.models.student import Student



class StudentBase(BaseModel):
    student_name: str



class StudentCreate(StudentBase):
    pass



class StudentView(StudentBase):
    student_id: int


    class Config:
        orm_mode = True