from data.database import read_query, insert_query, update_query
from my_models.model_user import Role, User
from my_models.model_player import Player
from authentication.authenticator import find_by_email
from my_models.model_admin_requests import AdminRequests
from my_models.model_director_requests import DirectorRequests
from services import email_service
from fastapi.responses import JSONResponse
from email_validator import validate_email
from services import shared_service
from services import player_service
from services import admin_service
from authentication.authenticator import create_token, get_user_or_raise_401
import random


_SEPARATOR = ';'


def _hash_password(password: str):
    ''' Used to hash a password of a user before saving it in the database.'''
    from hashlib import sha256
    return sha256(password.encode('utf-8')).hexdigest()


def logged_user(email:str, password: str):

    try:
        validate_email(email, check_deliverability=False)
    except:
        return JSONResponse(status_code=400, content='Email is not valid.')
    
    users_account = find_by_email(email)
    
    if users_account.is_verified == 0:
        return JSONResponse(status_code=401, content="Your account hasn't been verified!")
    
    user = try_login(email, password)

    if user:
        token = create_token(user)
        return {'token': token}
    else:
        return JSONResponse(status_code=400, content='Invalid login data!')


def try_login(email: str, password: str) -> User | None:
    ''' Used to hash the login password and compare it with the existing password of the user in the database.'''

    user = find_by_email(email)

    password = _hash_password(password)
    
    return user if user and user.password == password else None


def register_user(full_name: str, email: str, password: str, repeat_password: str, gender:str ):
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

    if shared_service.full_name_exists(full_name, 'users'): 
        return JSONResponse(status_code=400, content=f'The full name: {full_name} is already taken!')
    
    elif shared_service.email_exists(email):
        return JSONResponse(status_code=400, content=f'The email: {email} is already taken!')
    
    try:
        validate_email(email, check_deliverability=False)
    except:
        return JSONResponse(status_code=400, content='Email is not valid.')
    
    if len(password) < 6:
        return JSONResponse(status_code=400, content='Password must be at least 6 characters long.')
    
    elif password != repeat_password:
        return JSONResponse(status_code=400, content="The password doesn't match.")
    
    else:
        user = create(full_name, email, password, gender)
    
    return user


def create(full_name: str, email: str, password: str, gender: str) -> User | None:
    ''' Automatically creates id for the user and inserts all the user's data in the database in the row of the same id.
    
        Args:
        - full_name: str
        - email: str
        - hashed password: str
        - gender: str

        Returns:
            - Class User
    '''
    
    password = _hash_password(password)
    
    role = Role.SPECTATOR
    players_id = None
    is_verified = 0
    verification_code = random.randrange(0, 999999, 6)

    generated_id = insert_query(
        'INSERT INTO users(full_name, email, password, gender, role, players_id, is_verified, verification_code) VALUES (?,?,?,?,?,?,?,?)',
        (full_name, email, password, gender, role, players_id, is_verified, verification_code)
    )

    email_service.send_verification_email(email, verification_code)

    return User(id=generated_id, full_name=full_name, email=email, password='******', gender=gender, role=role, players_id=players_id, is_verified=is_verified, verification_code=000000)


def user_information(x_token: str):
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


def deleted_own_user_account(x_token: str):
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
        delete_account(user.id)
    elif User.is_director(user):
        delete_account(user.id)
    elif User.is_admin(user):
        return JSONResponse(status_code=401, content="Admin is not allowed to delete his/her's/it's account.")
    else:
        return JSONResponse(status_code=400, content='Unrecognized credentials.')
    
    return {'Your account has been deleted.'}


def delete_account(id: int):
    ''' Used for deleting user's own account from the database.'''

    insert_query('''DELETE FROM users WHERE id = ?''',
                 (id,))


def find_all_admin_requests(id: int) -> AdminRequests | None:
    ''' Search in the database and creates a list of all user's requests.
    
    Returns:
        - a list of all user's requests (id, type_of_request, players_id, users_id, status)
    '''

    data = read_query('SELECT id, type_of_request, players_id, users_id, status FROM admin_requests WHERE users_id = ?',
        (id,))

    return (AdminRequests.from_query_result(*row) for row in data)


def find_all_user_director_requests(id: int) -> DirectorRequests | None:
    ''' Search in the database and creates a list of all user's director requests.
    
    Returns:
        - a list of all user's director requests (id, full_name, country, sports_club, users_id, status)
    '''

    data = read_query('SELECT id, full_name, country, sports_club, users_id, status FROM director_requests WHERE users_id = ?',
        (id,))

    return (DirectorRequests.from_query_result(*row) for row in data)
    

def find_admin_request_by_id_and_users_id(id: int, users_id: int) -> AdminRequests | None:
    ''' Search in the database and returns user's requests by ID.
    
    Returns:
        - a request of user (id, type_of_request, players_id, users_id, status)
    '''

    data = read_query('SELECT id, type_of_request, players_id, users_id, status FROM admin_requests WHERE id = ? and users_id = ?',
        (id, users_id))

    return next((AdminRequests.from_query_result(*row) for row in data), None)


def send_connection_request(type_of_request:str, players_id:int, users_id:int) -> AdminRequests | None:
    ''' Creates an ID and saves the connection request in the database.
    
    Args:
        - type_of_request: str
        - players_id: int
        - users_id: int

    Returns:
        - created request for connection
    '''

    status = 'pending'

    generated_id = insert_query(
        'INSERT INTO admin_requests(type_of_request, players_id, users_id, status) VALUES (?,?,?,?)',
        (type_of_request, players_id, users_id, status)
    )

    return AdminRequests(id=generated_id, type_of_request=type_of_request, players_id=players_id, users_id=users_id, status=status)


def send_promotion_request(type_of_request:str, users_id:int) -> AdminRequests | None:
    ''' Creates an ID and saves the promotion request in the database.
    
    Args:
        - type_of_request: str
        - users_id: int

    Returns:
        - created request for promotion
    '''

    status = 'pending'
    generated_id = insert_query(
        'INSERT INTO admin_requests(type_of_request, users_id, status) VALUES (?,?,?)',
        (type_of_request, users_id, status)
    )
    # ДА СЕ ИЗПОЛЗВА КОГАТО АДМИН ОДОБРЯВА АДМИН REQUEST
    # is_active = 1
    # players_id = User.players_id #TODO
    # update_query('''UPDATE players SET is_active = ? WHERE id = ?''',
    #             (is_active, players_id))
    return AdminRequests(id=generated_id, type_of_request=type_of_request, users_id=users_id, status=status)


def send_creation_request(users_id:int, full_name: str, country: str, sports_club: str) -> DirectorRequests | None:
    ''' Creates an ID and saves the creation request in the database.
    
    Args:
        - users_id: int
        - full_name: str
        - country: str
        - sports_club: str

    Returns:
        - created request for creation
    '''

    status = 'pending'
    generated_id = insert_query(
        'INSERT INTO director_requests(full_name, country, sports_club, users_id, status) VALUES (?,?,?,?,?)',
        (full_name, country, sports_club, users_id, status)
    )

    return DirectorRequests(id=generated_id, full_name=full_name, country=country, sports_club=sports_club, users_id=users_id, status=status)


def get_user_full_name_by_id(user_id):
    user_name = read_query('SELECT full_name FROM users WHERE id = ?', (user_id,))
    return user_name[0][0]


def verificated_user(email: str, verification_code: str):
    ''' Used for user to verify his/hers/its account.

    Args:
        - email(str): Query
        - verification_code(int): Query

    Returns:
        - Verification
    '''

    try:
        validate_email(email, check_deliverability=False)
    except:
        return JSONResponse(status_code=400, content='Email is not valid.')
    
    verification = verify_account(email, verification_code)
    
    return verification


def verify_account(email: str, verification_code: int):

    is_verified = 0
    data = read_query('SELECT id, full_name, email, password, gender, role, players_id, is_verified, verification_code FROM users WHERE email = ? and is_verified = ? and verification_code = ?', (email, is_verified, verification_code))
    
    user = next((User.from_query_result(*row) for row in data), None)

    if user:
        is_verified = 1
        update_query('''UPDATE users SET is_verified = ? WHERE id = ?''',
                    (is_verified, user.id))
        email_service.send_email(email, 'verified')
        return {'You successfully verified your account.'}
    else:
        return JSONResponse(status_code=400, content='Your verification data is not valid.')


def get_director_requests_by_id(id: int):
    ''' Used to find a specific request in director_requests in the database.
    
    Args:
        - id(int)
    Returns:
        - director request from user
    '''

    data = read_query('SELECT id, full_name, country, sports_club, users_id, status FROM director_requests WHERE id = ?',
                      (id,))
    
    return (DirectorRequests.from_query_result(*row) for row in data)


def find_director_request_by_id_and_users_id(id: int, users_id: int) -> DirectorRequests | None:
    ''' Search in the database and returns user's director requests by ID.
    
    Returns:
        - a director request of user (id, full_name, country, sports_club, users_id, status)
    '''

    data = read_query('SELECT id, full_name, country, sports_club, users_id, status FROM director_requests WHERE id = ? and users_id = ?',
        (id, users_id))

    return next((DirectorRequests.from_query_result(*row) for row in data), None)


def create_director_request(country: str, sports_club: str, x_token: str):
    ''' Used for creating and sending a request for creating a player.

    Args:
        - country: str(Query)
        - sports_club: str(Query)
        - JWT token(Header)
    
    Returns:
        - Created director request
    '''
    
    user = get_user_or_raise_401(x_token)

    if shared_service.full_name_exists(user.full_name, 'players'):
        return JSONResponse(status_code=400, content=f"Player with full name: {user.full_name} already exists.")
    elif shared_service.director_request_exists(user.id):
        return JSONResponse(status_code=400, content='You already sent that kind of request, please wait for a response.')
    
    elif User.is_spectator(user):
        if User.is_verified_account(user):
            return send_creation_request(user.id, user.full_name, country, sports_club)
        else:
            return JSONResponse(status_code=401, content="Your account is not verified.")
        

def get_all_director_requests(x_token: str):
    ''' Used to get all sent and received creation requests.
    
    Args:
        - JWT token(Header)
    
    Returns:
        - list of all user's requests
    '''
    
    user = get_user_or_raise_401(x_token)
    user_id = user.id

    if not User.is_verified_account(user):
        return JSONResponse(status_code=401, content="Your account is not verified.")

    if User.is_admin(user):
        return find_all_director_requests()
    elif User.is_director(user):
        return find_all_director_requests()
    elif User.is_spectator(user):
        return find_all_user_director_requests(user_id)
    

def find_all_director_requests() -> DirectorRequests | None:
    ''' Used to take all requests in director_requests in the database.
    
    Returns:
        - list of director requests from users
    '''

    data = read_query('SELECT id, full_name, country, sports_club, users_id, status FROM director_requests')
    
    return (DirectorRequests.from_query_result(*row) for row in data)


def get_director_request_by_id(id: int, x_token: str):
    ''' Used to to get all sent and received user director requests.
    
    Args:
        - JWT token(Header)
    
    Returns:
        - Director request
    '''
    
    user = get_user_or_raise_401(x_token)

    if not shared_service.id_exists(id, 'director_requests'):
        return JSONResponse(status_code=404, content=f'Director request with ID: {id} does not exist.')
    elif not User.is_verified_account(user):
        return JSONResponse(status_code=401, content="Your account is not verified.")
    
    if User.is_admin(user):
        result = get_director_requests_by_id(id)
    elif User.is_director(user):
        result = get_director_requests_by_id(id)
    elif User.is_spectator(user):
        result = find_director_request_by_id_and_users_id(id, user.id)
    else:
        return JSONResponse(status_code=401, content='Unrecognized credentials!')

    if result == None:
        return JSONResponse(status_code=404, content=f'Director request with ID: {id} does not exist.')
    else:
        return result
    

def delete_director_request_by_id(id: int, x_token: str):
    ''' Used for deleting an already created director request for creating a players if the status is 'pending'.

    Args:
        - requests.id: int(URL link)
        - JWT token
    
    Returns:
        - Deleted director request
    '''
    
    if not shared_service.id_exists(id, 'director_requests'):
        return JSONResponse(status_code=404, content=f'Director request with ID: {id} does not exist.')
    
    user = get_user_or_raise_401(x_token)
    result = find_director_request_by_id_and_users_id(id, user.id)
    request = (shared_service.id_exists_director_requests(id).status)

    if not User.is_verified_account(user):
        return JSONResponse(status_code=401, content="Your account is not verified.")

    if request == 'pending':
        if User.is_spectator(user) and result.users_id == user.id:
            shared_service.delete_director_request(id)
        elif User.is_director(user): 
            shared_service.delete_director_request(id)
        elif User.is_admin(user):
            shared_service.delete_director_request(id)
        else:
            return JSONResponse(status_code=404, content='No director requests found.')
    else:
        return JSONResponse(status_code=400, content="You are not allowed to delete a director request if the status is different than 'pending'!")
        
    return {'The director request has been deleted.'}


def director_request_exists(full_name: str):
    ''' Used to check if the id exists in director_requests in the database.

    Returns:
        - Status from director_requests if the user_id exists, None otherwise.
    '''

    status = 'pending'

    result = read_query(
        'SELECT id, full_name, country, sports_club, users_id, status FROM director_requests WHERE full_name = ? and status = ?',
        (full_name, status)
    )

    result = next((DirectorRequests.from_query_result(*row, ) for row in result), None)

    return result


def update_director_request_status(new_status: str, full_name: str, old_status: str):

    update_query('''UPDATE director_requests SET status = ? WHERE full_name = ? and status = ?''',
                    (new_status, full_name, old_status))
    

def create_and_send_admin_request(type_of_request: str, players_id: int, x_token: str):
    ''' Used for creating and sending a request for connection or promotion.

    Args:
        - type_of_request: str(Query)
        - players_id: int(Query)
        - JWT token(Header)
    
    Returns:
        - Created admin request
    '''
    
    user = get_user_or_raise_401(x_token)
    users_id = user.id

    if type_of_request == 'connection':
        if User.is_spectator(user):
            if players_id == None:
                return JSONResponse(status_code=400, content="You must enter id of a player.")
            elif not User.is_verified_account(user):
                return JSONResponse(status_code=401, content="Your account is not verified.")
            elif user.players_id != None:
                return JSONResponse(status_code=400, content="You are already connected to a player name.")
            elif not shared_service.id_exists(players_id, 'players'):
                return JSONResponse(status_code=404, content=f'Player with id: {players_id} does not exist.')
            elif shared_service.user_connection_request_exists(users_id):
                return JSONResponse(status_code=400, content='You already sent that kind of request, please wait for a response.')
            
            player = player_service.get_player_by_id(players_id)
            if Player.is_connected_account(player):
                return JSONResponse(status_code=404, content=f'Player with id: {players_id} is already connected to another user.')
            
            return send_connection_request(type_of_request, players_id, users_id)
        else:
            return JSONResponse(status_code=401, content="You must be a spectator to be able to connect to your player's account.")
    
    elif type_of_request == 'promotion' and players_id == None:
        if shared_service.user_promotion_request_exists(users_id):
            return JSONResponse(status_code=400, content='You already sent that kind of request, please wait for a response.')
        elif User.is_director(user):
            return JSONResponse(status_code=400, content="Your user's account is already with a 'director' role!")
        elif not User.is_player(user):
            return JSONResponse(status_code=400, content="Only users with 'player' role can request to be promoted to 'director'!")
        else:
            return send_promotion_request(type_of_request, users_id)
    else:
        return JSONResponse(status_code=400, content="Unrecognized type of request!")
    

def get_all_admin_requests(x_token: str):
    ''' Used to get all sent and received user requests.
    
    Args:
        - JWT token(Header)
    
    Returns:
        - list of all user's requests
    '''
    
    user = get_user_or_raise_401(x_token)
    user_id = user.id

    if User.is_admin(user):
        return admin_service.get_all_admin_requests()
    elif not User.is_verified_account(user):
        return JSONResponse(status_code=401, content="Your account is not verified.")
       
    return find_all_admin_requests(user_id)


def get_admin_request_by_id(id: int, x_token: str):
    ''' Used to to get all sent and received user requests.
    
    Args:
        - JWT token(Header)
    
    Returns:
        - user's request
    '''
    
    user = get_user_or_raise_401(x_token)

    if not shared_service.id_exists(id, 'admin_requests'):
        return JSONResponse(status_code=404, content=f'Request with ID: {id} does not exist.')
    elif not User.is_verified_account(user):
        return JSONResponse(status_code=401, content="Your account is not verified.")
    
    if User.is_admin(user):
        result = admin_service.get_admin_request_by_id(id)
    elif User.is_spectator(user):
        result = find_admin_request_by_id_and_users_id(id, user.id)
    elif User.is_player(user):
        result = find_admin_request_by_id_and_users_id(id, user.id)
    else:
        return JSONResponse(status_code=401, content='Unrecognized credentials!')

    if result == None:
        return JSONResponse(status_code=404, content=f'Request with ID: {id} does not exist.')
    else:
        return result
    

def delete_admin_request_by_id(id: int, x_token: str):
    ''' Used for deleting an already created request for connection or promotion if the status is 'pending'.

    Args:
        - requests.id: int(URL link)
        - JWT token
    
    Returns:
        - Deleted request
    '''
    
    user = get_user_or_raise_401(x_token)

    if not shared_service.id_exists(id, 'admin_requests'):
        return JSONResponse(status_code=404, content=f'Request with ID: {id} does not exist.')
    elif not User.is_verified_account(user):
        return JSONResponse(status_code=401, content="Your account is not verified.")
    
    request = (shared_service.id_exists_admin_requests(id).status)

    if request == 'pending':
        if User.is_spectator(user):
            shared_service.delete_admin_request(id)
        elif User.is_player(user): 
            shared_service.delete_admin_request(id)
        elif User.is_admin(user):
            request_info = shared_service.id_exists_admin_requests_full_info(id)
                
            if request_info.type_of_request == 'connection':
                email_type = 'link_profile_declined'
            elif request_info.type_of_request == 'promotion':
                email_type = 'promotion_declined'

            data = read_query('SELECT users_id FROM admin_requests WHERE id = ? and status = ?',
                (id, request))

            email = read_query('SELECT email FROM users WHERE id = ?',
                (data,))
                
            email_service.send_email(email, email_type)

            shared_service.delete_admin_request(id)
    
        else:
            return JSONResponse(status_code=404, content='No requests found.')
    else:
        return JSONResponse(status_code=400, content="You are not allowed to delete a request if it's status is different than 'pending'!")
        
    return {'The request has been deleted.'}


def players_id_exists_in_users(players_id: int, full_name: str):
    ''' Used to check if the players_id exists in users.

    Returns:
        - user
    '''

    data = read_query('SELECT id, full_name, email, password, gender, role, players_id, is_verified, verification_code FROM users WHERE players_id = ? and full_name = ?',
        (players_id, full_name))

    return next((User.from_query_result_no_password(*row, ) for row in data), None)
