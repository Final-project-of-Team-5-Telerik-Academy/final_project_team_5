from fastapi import APIRouter, Header, Query
from services import user_service
from services import shared_service
from authentication.authenticator import get_user_or_raise_401, create_token
from my_models.model_user import User
from fastapi.responses import JSONResponse
from email_validator import validate_email


users_router = APIRouter(prefix='/users', tags={'Everything available for Users.'})


@users_router.post('/register', description='Please enter your personal information')
def register(full_name: str = Query(..., description='Enter your full name:'),
             email: str = Query(..., description='Enter your email address:'),
             password: str = Query(..., description='Enter your password: (It has to be at least 6 characters!)'),
             re_password: str = Query(..., description='Re enter your password for validation:'),
             gender: str = Query(..., description='Choose a gender: male/female/non-binary')):
    ''' Used for registering new users.
    
    Args:
        - full_name(str): Query
        - email(str): Query
        - password(str): Query
        - re_password(str): QUery
        - gender(str): Query
    
    Returns:
        - Registered user as a default spectator role
    '''    

    if shared_service.full_name_exists(full_name, 'users'): 
        return JSONResponse(status_code=400, content=f'The full name: {full_name} is already taken!')
    
    if shared_service.email_exists(email):
        return JSONResponse(status_code=400, content=f'The email: {email} is already taken!')
    
    try:
        validate_email(email, check_deliverability=False)
    except:
        return JSONResponse(status_code=400, content='Email is not valid.')
    
    if len(password) < 6:
        return JSONResponse(status_code=400, content='Password must be at least 6 characters long.')
    
    if password != re_password:
        return JSONResponse(status_code=400, content="The password doesn't match.")
    
    if gender != 'male' and gender != 'female' and gender != 'non-binary' and gender != 'Male' and gender != 'Female' and gender != 'Non-binary':
        return JSONResponse(status_code=404, content="Gender must be one of the following: 'male', 'female' or 'non-binary'.")

    user = user_service.create(full_name, email, password, gender)
    
    return user


@users_router.post('/login', description='Please enter your personal information')
def login(email: str = Query(..., description='Enter your email address:'), 
          password: str = Query(..., description='Enter your password:')):
    ''' Used for logging in.

    Args:
        - email(str): Query
        - password(str): Query

    Returns:
        - JWT token
    '''
    
    try:
        validate_email(email, check_deliverability=False)
    except:
        return JSONResponse(status_code=400, content='Email is not valid.')
    
    user = user_service.try_login(email, password)

    if user:
        token = create_token(user)
        return {'token': token}
    else:
        return JSONResponse(status_code=400, content='Invalid login data!')


@users_router.get('/info', description='Your personal user information.')
def my_user_information(x_token: str = Header(default=None)):
    ''' Used to see information about the profile.
    
    Args:
        - JWT token(Header)
    
    Returns:
        - user(id, full_name, email, gender, role and players_id)
    '''
    
    if x_token == None:
        return JSONResponse(status_code=401, content='You must be logged in to view your personal information.')
    
    user = get_user_or_raise_401(x_token)

    # За ендпойнт: info/{id}
    # if not utils_service.id_exists(id, 'users'):
    #     raise JSONResponse(status_code=404, detail=f'User with id {id} does not exist.')
    
    return User(id=user.id, full_name=user.full_name, email=user.email, password='******', gender=user.gender, role=user.role, players_id=user.players_id)


@users_router.delete('/delete')
def delete_own_account(x_token: str = Header(default=None)):
    ''' Used for deleting own account.

    Args:
        - JWT token(Header)
    
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
        return JSONResponse(status_code=401, content="Admin is not allowed to delete his/her's/it's account.")
    else:
        return JSONResponse(status_code=400, content='Unrecognized credentials.')
    
    return {'Your account has been deleted.'}


@users_router.post('/matchrequest', description="Please fill the form to send a match request to another user with connected player's account")
def match_request(message: str = Query(default=None, description='Enter your message:'),
             receiver_id: int = Query(..., description='To whom do you want to send the friendly match request?'),
             x_token: str = Header(default=None)):
    ''' Used to send a friendly match request to another user with a connected player's account.
    
    Args:
        - message(str): Query
        - receiver_id(int): Query
        - JWT token(Header)
    
    Returns:
        - Created friendly match request
    '''

    if x_token == None:
        return JSONResponse(status_code=401, content='You must be logged in to send a friendly match request.')    
    
    user = get_user_or_raise_401(x_token)

    if User.is_player(user):
        if not shared_service.id_exists(receiver_id, 'users'):
            return JSONResponse(status_code=400, content=f'User with id: {receiver_id} does not exist.')
        if user.players_id == None:
            return JSONResponse(status_code=401, content=f"Your user's account is not connected to a player's account. Only Users linked to their players accounts are allowed to send friendly match requests.")
        if message == None:
            return JSONResponse(status_code=400, content='You must write a message.')
        # проверка дали е активен player акаунта
        
        sender_id = user.id
        result = user_service.send_friendly_match_request(message, sender_id, receiver_id)
        
    else:
        return JSONResponse(status_code=401, content="Only users with connected player's account and with 'player' role can send a friendly match request.")
    
    return result
    

@users_router.get('/matchrequest', description='All friendly match requests.')
def all_match_requests(option: str = Query(default=None, description="Choose between 'sent' and 'received':"),
                                x_token: str = Header(default=None)):
    ''' Used to to get all sent and received friendly match requests.
    
    Args:
        - JWT token(Header)
    
    Returns:
        - list of all friendly match requests
    '''

    if x_token == None:
        return JSONResponse(status_code=401, content='You must be logged in to be able to see your sent and received friendly match requests.')
    
    user = get_user_or_raise_401(x_token)
    
    if not User.is_player(user):
        return JSONResponse(status_code=401, content="Only user's with connected player's accounts and 'player' role are allowed see their sent and received friendly match requests.")
    
    if option != 'sent' and option != 'received':
        return JSONResponse(status_code=400, content="Unrecognized command.")
    
    if option == 'sent':
        return user_service.find_all_sent_friendly_match_requests(user.id)
    
    elif option == 'received':
        return user_service.find_all_received_friendly_match_requests(user.id)