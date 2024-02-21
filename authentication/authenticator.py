from fastapi import HTTPException
from fastapi.responses import JSONResponse
from my_models.model_user import User
from data.database import read_query
import jwt
from datetime import datetime, timedelta


_JWT_SECRET = ';a,jhsd1jahsd1kjhas1kjdh'


def get_user_or_raise_401(token: str) -> User:
    ''' Authenticates the given token in Header and finds the whole information of the user through its full name:
    
    Args:
        - token (str): text with indents
    '''

    try:
        payload = is_authenticated(token)

        expiration_time = payload['exp']
        if datetime.utcnow() > datetime.utcfromtimestamp(expiration_time):
            raise HTTPException(status_code=401, detail="Token has expired.")
        
        return find_by_email(payload['email'])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired.")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token.")
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid credentials.")
    

def find_by_email(email: str) -> User | None:
    ''' Drags the id from the token so it can be compared.

    Args:
        - token (str): text with indents

    Returns:
        - id of the token
    '''

    data = read_query(
        'SELECT id, full_name, email, password, gender, role, players_id, is_verified, verification_code FROM users WHERE email = ?',
        (email,))
    
    return next((User.from_query_result(*row) for row in data), None)
    

def find_by_id(id: int) -> User | None:
    ''' Search through user.id the whole information about the account in the data.
     
    Args:
        - id: int 
        
    Returns:
        - all the necessary information about the user (id, full_name, email, password, gender, role, is_verified, verification_code)
    '''

    data = read_query(
        'SELECT id, full_name, email, password, gender, role, players_id, is_verified, verification_code FROM users WHERE id = ?',
        (id,))

    return next((User.from_query_result(*row) for row in data), None)


def create_token(user: User) -> str:
    ''' Creates JWT token when user uses login request.
    
    Args:
        - user: id(int), email(str), exp: (datetime, timedelta)
    
    Returns:
        - encoded JWT token
    '''

    expiration_time = datetime.utcnow() + timedelta(minutes=30000)

    payload = {
        "id": user.id,
        "email": user.email,
        "exp": expiration_time
    }
   
    return jwt.encode(payload, _JWT_SECRET, algorithm="HS256")


def is_authenticated(token: str) -> bool:
    ''' Decodes JWT token.
    
    Args:
        - encoded JWT token
    
    Returns:
        - decoded JWT token
    '''

    return jwt.decode(token, _JWT_SECRET, algorithms=["HS256"])
