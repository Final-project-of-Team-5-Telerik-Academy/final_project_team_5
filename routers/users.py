from fastapi import APIRouter, Header, Query
from services import user_service
from services import shared_service
from authentication.authenticator import get_user_or_raise_401, create_token
from my_models.model_user import User
from fastapi.responses import JSONResponse
from email_validator import validate_email
from services.player_service import get_player_by_id



users_router = APIRouter(prefix='/users', tags={'Users'})


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

    
@users_router.post('/requests/create', description="Please fill the form to send a connection/promotion request:")
def create_request(type_of_request: str = Query(default=None, description="Choose between 'connection' or 'promotion':"),
             players_id: int = Query(default=None, description="Enter ID of the player's account:"),
             x_token: str = Header(default=None)):
    ''' Used for creating and sending a request for connection or promotion.

    Args:
        - type_of_request: str(Query)
        - players_id: int(Query)
        - JWT token(Header)
    
    Returns:
        - Created request
    '''

    if x_token == None:
        return JSONResponse(status_code=401, content='You must be logged in to send a connection/promotion request.')    
    
    user = get_user_or_raise_401(x_token)
    users_id = user.id

    if type_of_request == 'connection':
        if User.is_spectator(user):
            if players_id == None:
                return JSONResponse(status_code=400, content="You must enter id of a player.")
            if user.players_id != None:
                return JSONResponse(status_code=400, content="You are already connected to a player name.")
            if not shared_service.id_exists(players_id, 'players'):
                return JSONResponse(status_code=404, content=f'Player with id: {players_id} does not exist.')
            if shared_service.user_connection_request_exists(users_id):
                return JSONResponse(status_code=400, content='You already sent that kind of request, please wait for your response.')
            
            player = get_player_by_id(players_id)
            if player.is_connected == 1:
                return JSONResponse(status_code=404, content=f'Player with id: {players_id} is already connected to another user.')
            
            return user_service.send_connection_request(type_of_request, players_id, users_id)
        else:
            return JSONResponse(status_code=401, content="You must be a spectator to be able to connect to your player's account.")
    
    elif type_of_request == 'promotion' and players_id == None:
        if shared_service.user_promotion_request_exists(users_id):
                return JSONResponse(status_code=400, content='You already sent that kind of request, please wait for your response.')
        if User.is_player(user):
            return user_service.send_promotion_request(type_of_request, users_id)
        return JSONResponse(status_code=401, content=f"Your user account is with '{user.role}'! Your role must be 'player' to be able to request of promotion.")
    else:
        return JSONResponse(status_code=400, content="Unrecognized type of request!")
        

@users_router.delete('/requests/delete')
def delete_request(id: int = Query(..., description='Enter ID of the request you want to delete:'), 
                x_token: str = Header(default=None)
                ):
    ''' Used for deleting an already created request for connection or promotion if the status is 'pending'.

    Args:
        - requests.id: int(URL link)
        - JWT token
    
    Returns:
        - Deleted request
    '''

    if x_token == None:
        return JSONResponse(status_code=401, content='You must be logged in delete your request.')    
    
    user = get_user_or_raise_401(x_token)

    if not shared_service.id_exists(id, 'admin_requests'):
        return JSONResponse(status_code=404, content=f'Request with id: {id} does not exist.')
    
    request = (shared_service.id_exists_requests(id).status)

    if request == 'pending':
        if User.is_spectator(user):
            shared_service.delete_request(id)
        elif User.is_player(user): 
            shared_service.delete_request(id)
        else:
            return JSONResponse(status_code=404, content='No requests found.')
    else:
        return JSONResponse(status_code=400, content="You are not allowed to delete a request if it's status is different than 'pending'!")
        
    return {'Your request has been deleted.'}



@users_router.get('/requests', description='View all your requests:')
def all_user_requests(x_token: str = Header(default=None)):
    ''' Used to to get all sent and received user requests.
    
    Args:
        - JWT token(Header)
    
    Returns:
        - list of all user's requests
    '''

    if x_token == None:
        return JSONResponse(status_code=400, content='You must be logged in to see your requests!')
    
    user = get_user_or_raise_401(x_token)
    user_id = user.id
       
    return user_service.find_all_user_requests(user_id)


@users_router.get('/requests/id', description='View specific request:')
def find_request_by_id(request_id: int = Query(..., description='Enter ID of the request you want to view:'),
                      x_token: str = Header(default=None)):
    ''' Used to to get all sent and received user requests.
    
    Args:
        - JWT token(Header)
    
    Returns:
        - list of all user's requests
    '''

    if x_token == None:
        return JSONResponse(status_code=400, content='You must be logged in to see your requests!')
    
    user = get_user_or_raise_401(x_token)
       
    result = user_service.find_request_by_id(request_id, user.id)

    if result == None:
        return JSONResponse(status_code=404, content='Request not found!')
    
    return result