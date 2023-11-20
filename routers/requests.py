from fastapi import APIRouter, Header, Query
from services import user_service
from services import shared_service
from services import admin_service
from authentication.authenticator import get_user_or_raise_401
from my_models.model_user import User
from fastapi.responses import JSONResponse
from services.player_service import get_player_by_id


requests_router = APIRouter(prefix='/requests', tags={'Requests'})


@requests_router.post('/', description="Please fill the form to create and send a connection/promotion request:")
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
        if User.is_director(user):
            return JSONResponse(status_code=400, content="Your user's account is already with a 'director' role!")
        if not User.is_player(user):
            return JSONResponse(status_code=400, content="Only users with 'player' role can request to be promoted to 'director'!")
        else:
            return user_service.send_promotion_request(type_of_request, users_id)
    else:
        return JSONResponse(status_code=400, content="Unrecognized type of request!")


@requests_router.get('/', description='View all your requests:')
def find_all_requests(x_token: str = Header(default=None)):
    ''' Used to get all sent and received user requests.
    
    Args:
        - JWT token(Header)
    
    Returns:
        - list of all user's requests
    '''

    if x_token == None:
        return JSONResponse(status_code=400, content='You must be logged in to see your requests!')
    
    user = get_user_or_raise_401(x_token)
    user_id = user.id

    if User.is_admin(user):
        return admin_service.get_all_requests()
       
    return user_service.find_all_user_requests(user_id)


@requests_router.get('/id', description='View specific request:')
def find_request_by_id(id: int = Query(..., description='Enter ID of the request you want to view:'),
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

    if not shared_service.id_exists(id, 'admin_requests'):
        return JSONResponse(status_code=404, content=f'Request with ID: {id} does not exist.')
    
    if User.is_admin(user):
        result = admin_service.get_requests_by_id(id)
    elif User.is_spectator(user):
        result = user_service.find_request_by_id_and_users_id(id, user.id)
    elif User.is_player(user):
        result = user_service.find_request_by_id_and_users_id(id, user.id)
    else:
        return JSONResponse(status_code=401, content='Unrecognized credentials!')

    if result == None:
        return JSONResponse(status_code=404, content=f'Request with ID: {id} does not exist.')
    else:
        return result
    

@requests_router.delete('/', description="Please fill the form to delete your request:")
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
        return JSONResponse(status_code=404, content=f'Request with ID: {id} does not exist.')
    
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

