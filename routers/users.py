from fastapi import APIRouter, Header, Query
from services import user_service
from authentication.authenticator import get_user_or_raise_401
from datetime import date
from my_models.model_user import UserResult,User
from fastapi.responses import JSONResponse


users_router = APIRouter(prefix='/user',tags={'Everything available for Users'})

@users_router.post('/register', description= 'You can register from here using your email.')
def register(email: str  = Query(), 
             username: str = Query(), 
             password: str = Query(description='The password has to be longer than 5 characters!'), 
             date_of_birth: date = Query(description='Please state your date of birth using the (-) symbol',default='1998-11-11'), 
             gender: str = Query(description='Choose a gender male/female/non-binary')):

    if user_service.check_email_exist(email):
        return JSONResponse(status_code=400, content=f'This email is already taken!')

    if user_service.check_username_exist(username):
        return JSONResponse(status_code=400, content=f'This nickname is already taken!')
    else:
        user = user_service.create_user(email, username, password, date_of_birth,gender)
        return user

@users_router.post('/login', description='You can login from here using your username and password.')
def login(username: str = Query(),password: str = Query()):
    user = user_service.try_login(username, password)

    if user:
        token = user_service.create_token(user)
        return {'token': token}
    else:
        return JSONResponse(status_code=404, content='Invalid login data')

@users_router.get('/info',description='Your personal user information.')
def my_user_information(x_token: str = Header()):
    
    user = get_user_or_raise_401(x_token)

    return User(id=user.id,email = user.email,nickname = user.nickname, password = user.password, date_of_birth= user.date_of_birth, gender = user.gender)