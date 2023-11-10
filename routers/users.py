from fastapi import APIRouter, Header, Query
from services import user_service
from services import util_service
from authentication.authenticator import get_user_or_raise_401, create_token
from my_models.model_user import User
from fastapi.responses import JSONResponse


users_router = APIRouter(prefix='/users', tags={'Everything available for Users.'})


@users_router.post('/register', description='You can register from here using your email.')
def register(full_name: str = Query(..., description="Full name of the user."),
             email: str = Query(..., description="User's email address."),
             password: str = Query(..., description='The password has to be at least 6 characters!'),
             gender: str = Query(..., description='Choose a gender male/female/non-binary.')):
    ''' Used for registering new users.
    
    Args:
        - full_name(str): Query
        - email(str): Query
        - password(str): Query
        - gender(str): Query
    
    Returns:
        - Registered user as a spectator role
    '''    

    if util_service.email_exists(email):
        return JSONResponse(status_code=400, content=f'This email is already taken!')
    
    if '@' not in email:
            return JSONResponse(status_code=400, content="Email must contain '@' sign.")

    if util_service.full_name_exists(full_name, 'users'): 
        return JSONResponse(status_code=400, content=f'This full name is already taken!')
    else:
        user = user_service.create(full_name, email, password, gender)
        return user


@users_router.post('/login', description='You can login from here using your email and your password.')
def login(email: str = Query(), password: str = Query()):
    ''' Used for logging in.

    Args:
        - email(str): Query
        - password(str): Query

    Returns:
        - JWT token
    '''

    user = user_service.try_login(email, password)

    if user:
        token = create_token(user)
        return {'token': token}
    else:
        return JSONResponse(status_code=404, content='Invalid login data!')


@users_router.get('/info', description='Your personal user information.')
def my_user_information(x_token: str = Header(default=None)):
    
    if x_token == None:
        raise JSONResponse(status_code=401, detail='You must be logged in to view your personal user information.')
    
    user = get_user_or_raise_401(x_token)

    # За ендпойнт: info/{id}
    # if not utils_service.id_exists(id, 'users'):
    #     raise JSONResponse(status_code=404, detail=f'User with id {id} does not exist.')
    
    return User(id=user.id, full_name=user.full_name, email=user.email, password='******', gender=user.gender, role=user.role)


@users_router.delete('/delete')
def delete_own_account(x_token: str = Header(default=None)):
    ''' Used for deleting own account.

    Args:
        - JWT token
    
    Returns:
        - Deleted user
    '''

    if x_token == None:
        return JSONResponse(status_code=401, content='You must be logged in to delete your account.')    
    
    user = get_user_or_raise_401(x_token)
    
    if User.is_spectator(user):
        user_service.delete_account(user.id)
    elif User.is_director(user):
        user_service.delete_account(user.id)
    elif User.is_admin(user):
        user_service.delete_account(user.id)
    else:
        return JSONResponse(status_code=404, content='Unrecognized credentials.')
    
    return {'Your account has been deleted.'}