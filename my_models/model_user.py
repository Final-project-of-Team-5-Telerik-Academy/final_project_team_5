from datetime import date
from pydantic import BaseModel,validator
from fastapi import HTTPException


class User(BaseModel):
    id: int
    email: str
    nickname: str
    password: str
    date_of_birth: date = None
    gender: str

    @validator('password')
    def validate_password_length(cls, value):
        if len(value) < 6:
            raise HTTPException(
                status_code=400,
                detail="Password must be at least 6 characters long",
            )
        return value
    
    @validator("gender")
    def validate_gender(cls, value):
        if value not in ["male", "female", "non-binary","Male","Female","Non-binary"]:
            raise HTTPException(status_code=404,detail="Gender must be one of these: 'male', 'female', 'non-binary'")
        return value

    @classmethod
    def from_query_result(cls, id, email,nickname, password,date_of_birth, gender):
        return cls(
            id=id,
            email=email,
            nickname = nickname,
            password=password,
            date_of_birth=date_of_birth,
            gender=gender)

class UserResult(BaseModel):
    id: int
    username: str
    score: int