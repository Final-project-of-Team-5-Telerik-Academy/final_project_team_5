from pydantic import BaseModel


class Role:
    SPECTATOR = 'spectator'
    PLAYER = 'player'
    DIRECTOR = 'director'
    ADMIN = 'admin'


class Verify:
    VERIFIED = 1


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
    is_verified: int | None = 0
    verification_code: int | None = None


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
    

    def is_verified_account(self):
        ''' Compares the user's account if it's verified through email.
        
        Returns:
            - True/False
        '''

        return self.is_verified == Verify.VERIFIED


    @classmethod
    def from_query_result(cls, id, full_name, email, password, gender, role, players_id, is_verified, verification_code):
        ''' When query is used in another function.
        
        Returns:
            - id, full_name, email, password, gender, role, players_id, is_verified, verification_code
        '''

        return cls(
            id=id,
            full_name=full_name,
            email=email,
            password=password,
            gender=gender,
            role=role,
            players_id=players_id,
            is_verified=is_verified,
            verification_code=verification_code
            )
    

    @classmethod
    def from_query_result_no_password(cls, id, full_name, email, password, gender, role, players_id, is_verified, verification_code):
        ''' When User Model is shown in the response.
        
        Returns:
            - id, full_name, email, password as '******', gender, role, players_id, is_verified, verification_code
        '''

        return cls(
            id=id,
            full_name=full_name,
            email=email,
            password='******',
            gender=gender,
            role=role,
            players_id=players_id,
            is_verified=0,
            verification_code=0
            )
