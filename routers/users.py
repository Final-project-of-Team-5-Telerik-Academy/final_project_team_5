from fastapi import APIRouter, Header, Query, Form
from services import user_service


users_router = APIRouter(prefix='/users', tags={'Users'})


@users_router.post('/register', description='Please enter your personal information:')
def register(full_name: str = Query(..., description='Enter your full name:'),
             email: str = Query(..., description='Enter your email address:'),
             password: str = Query(..., description='Enter your password: (It has to be at least 6 characters!)'),
             repeat_password: str = Query(..., description='Re enter your password for validation:'),
             gender: str = Form(..., description='Choose a gender:',example='male', enum = ['male', 'female', 'non-binary'])):
    ''' Used for registering new users.
    
    Args:
        - full_name(str): Query
        - email(str): Query
        - password(str): Query
        - repeat_password(str): QUery
        - gender(str): Query
    
    Returns:
        - Registered user as a default spectator role
    '''    

    return user_service.register_user(full_name, email, password, repeat_password, gender)


@users_router.post('/verification', description='Please fill your personal information to verify your account:')
def verification(email: str = Query(..., description='Enter your email address:'), 
          verification_code: int = Query(..., description='Enter your verification code:')):
    ''' Used for user to verify his/hers/its account.

    Args:
        - email(str): Query
        - verification_code(int): Query

    Returns:
        - Verification
    '''
    
    return user_service.verificated_user(email, verification_code)


@users_router.post('/login', description='Please enter your personal information:')
def login(email: str = Query('steven.atkinson@gmail.com', description='Enter your email address:'),
          password: str = Query('steven1', description='Enter your password:')):
    ''' Used for logging in.

    Args:
        - email(str): Query
        - password(str): Query

    Returns:
        - JWT token
    '''
    
    return user_service.logged_user(email, password)
    

@users_router.get('/info', description='Your personal user information:')
def my_user_information(x_token: str = Header(default=None)):
    ''' Used to see information about the profile.
    
    Args:
        - JWT token(Header)
    
    Returns:
        - user(id, full_name, email, gender, role and players_id)
    '''
    
    return user_service.user_information(x_token)


@users_router.delete('/delete', description='Delete your own user account:')
def delete_own_account(x_token: str = Header(default=None)):
    ''' Used for deleting own account.

    Args:
        - JWT token(Header)
    
    Returns:
        - Deleted user
    '''

    return user_service.deleted_own_user_account(x_token)
