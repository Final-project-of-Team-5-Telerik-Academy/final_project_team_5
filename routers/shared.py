from fastapi import APIRouter, Header, Query
from services import shared_service
from authentication.authenticator import get_user_or_raise_401
from my_models.model_user import User
from fastapi.responses import JSONResponse


shared_router = APIRouter(prefix='/shared_users', tags={'Shared Users'})


@shared_router.post('/create_player', description='Create a new player')
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
        created_player = shared_service.create_player(full_name, country, sports_club)
    elif User.is_admin(user):
        created_player = shared_service.create_player(full_name, country, sports_club)
    else:
        return JSONResponse(status_code=401, content='You must be an admin or a director to be able to create a player.')

    return created_player