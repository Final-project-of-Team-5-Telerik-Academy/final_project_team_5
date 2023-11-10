from pydantic import BaseModel, validator, constr
from fastapi import HTTPException
# import re


class Role:
    SPECTATOR = 'spectator'
    DIRECTOR = 'director'
    ADMIN = 'admin'


class LoginData(BaseModel):
    email: str
    password: str


class User(BaseModel):
    id: int | None = None
    full_name: str
    email: str
    password: str
    gender: str
    role: str | None = None
    players_id: int | None = None


    @validator('password')
    def validate_password_length(cls, password):
        if len(password) < 6:
            raise HTTPException(status_code=400, detail='Password must be at least 6 characters long.')
        return password
    

    @validator('gender')
    def validate_gender(cls, value):
        if value not in ['male', 'female', 'non-binary', 'Male', 'Female', 'Non-binary']:
            raise HTTPException(status_code=404, detail="Gender must be one of these: 'male', 'female' or 'non-binary'.")
        return value


    def is_spectator(self):
        ''' Compares the user's role if it's a spectator when a JWT token is written in the Header.
        
        Returns:
            - True/False
        '''

        return self.role == Role.SPECTATOR


    def is_director(self):
        ''' Compares the user's role if it's a director when a JWT token is written in the Header.
        
        Returns:
            - True/False
        '''

        return self.role == Role.DIRECTOR


    def is_admin(self):
        ''' Compares the user's role if it's an admin when a JWT token is written in the Header.
        
        Returns:
            - True/False
        '''

        return self.role == Role.ADMIN


    @classmethod
    def from_query_result(cls, id, full_name, email, password, gender, role, players_id):
        ''' When query is used in another function.
        
        Returns:
            - id, full_name, email, password, gender, role, players_id
        '''

        return cls(
            id=id,
            full_name=full_name,
            email=email,
            password=password,
            gender=gender,
            role=role,
            players_id=players_id
            )
    

    @classmethod
    def from_query_result_no_password(cls, id, full_name, email, password, gender, role, players_id):
        ''' When User Model is shown in the response.
        
        Returns:
            - id, full_name, email, password as '******', gender, role, players_id
        '''

        return cls(
            id=id,
            full_name=full_name,
            email=email,
            password='******',
            gender=gender,
            role=role,
            players_id=players_id
            )
