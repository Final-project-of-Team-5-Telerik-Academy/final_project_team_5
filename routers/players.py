from fastapi import APIRouter, Header, Query
from services import shared_service
from authentication.authenticator import get_user_or_raise_401
from my_models.model_user import User
from fastapi.responses import JSONResponse
from services import player_service


players_router = APIRouter(prefix='/players', tags={'Players'})


@players_router.post('/', description='Create a new player:')
def create_player(full_name: str = Query(..., description='Enter full name of player:'),
                  country: str = Query(..., description='Enter country of player:'),
                  sports_club: str = Query(..., description='Enter sport club of player:'),
                  x_token: str = Header(default=None)):
    ''' Used for creating a new player by a director or admin.

    Args:
        - full_name: str(Query)
        - country: str(Query)
        - sports_club: str(Query)
        - x_token: JWT token(Header)

    Returns:
        - Created player information
    '''

    if x_token == None:
        return JSONResponse(status_code=401, content='You must be logged in and be an admin to be able to create a player.')    
    
    user = get_user_or_raise_401(x_token)
    
    if User.is_director(user):
        created_player = player_service.create_player(full_name, country, sports_club)
    elif User.is_admin(user):
        created_player = player_service.create_player(full_name, country, sports_club)
    else:
        return JSONResponse(status_code=401, content='You must be an admin or a director to be able to create a player.')

    return created_player


@players_router.get('/', description= 'Show all players:')
def find_all_players(x_token: str = Header(default=None, description='Your identification token:')):
    
    if x_token is None:
        return JSONResponse(status_code=401, content='You must be logged in to view the list of players.')
    
    user = get_user_or_raise_401(x_token)

    if User.is_spectator(user):
        list_of_players = player_service.get_all_players()
    elif User.is_player(user):
        list_of_players = player_service.get_all_players()
    elif User.is_director(user):
        list_of_players = player_service.get_all_players()
    elif User.is_admin(user):
        list_of_players = player_service.get_all_players()
    else: 
        return JSONResponse(status_code=401, content='Unrecognized credentials.')

    return list_of_players


@players_router.get('/id', description='Find player:')
def find_player_by_id(id:int = Query(..., description='Enter id of the player:'), x_token: str = Header(default=None)):
    
    if x_token is None:
        return JSONResponse(status_code=401, content='You must be logged in to see the players information.')
    
    user = get_user_or_raise_401(x_token)

    if not shared_service.id_exists(id, 'players'):
            return JSONResponse(status_code=404, content=f'Player with id: {id} does not exist.')
    if User.is_spectator(user):
        player = player_service.get_player_by_id(id)
    elif User.is_player(user):
        player = player_service.get_player_by_id(id)
    elif User.is_director(user):
        player = player_service.get_player_by_id(id) 
    elif User.is_admin(user):
        player = player_service.get_player_by_id(id)
    else: 
        return JSONResponse(status_code=401, content='Unrecognized credentials.')
    return player