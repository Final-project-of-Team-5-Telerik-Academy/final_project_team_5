from pydantic import BaseModel
from fastapi import HTTPException


class Role:
    SPECTATOR = 'spectator'
    PLAYER = 'player'
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


    def is_spectator(self):
        ''' Compares the user's role if it's a spectator when a JWT token is written in the Header.
        
        Returns:
            - True/False
        '''

        return self.role == Role.SPECTATOR
    
    def is_player(self):
        ''' Compares the user's role if it's a player when a JWT token is written in the Header.
        
        Returns:
            - True/False
        '''

        return self.role == Role.PLAYER


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
