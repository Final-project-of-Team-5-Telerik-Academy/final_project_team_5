from fastapi import APIRouter, Header, Query, Form
from services import player_service
from my_models import countries, sport_clubs


players_router = APIRouter(prefix='/players', tags={'Players'})


@players_router.post('/', description='Create a new player:')
def create_player(full_name: str = Query(..., description='Enter full name of player:'),
                  country: str = Form(..., description='Choose a country:',example='Bulgaria', enum=countries.countries),
                  sports_club: str = Form(..., description='Choose a club sport:', example='Tenis Stars', enum=sport_clubs.sport_clubs),
                  x_token: str = Header()):
    ''' Used for creating a new player by a director or admin.

    Args:
        - full_name: str(Query)
        - country: str(Query)
        - sports_club: str(Query)
        - x_token: JWT token(Header)

    Returns:
        - Created player information
    '''

    return player_service.create_player_account(full_name, country, sports_club, x_token)


@players_router.get('/', description= 'Show all players:')
def find_all_players(x_token: str = Header(..., description='Your identification token:')):
    ''' Used to get all player accounts.
    
    Args:
        - JWT token(Header)
    
    Returns:
        - list of all player accounts
    '''

    return player_service.find_all_player_accounts(x_token)


@players_router.get('/id', description='Find player:')
def find_player_by_id(id:int = Query(..., description='Enter id of the player:'), x_token: str = Header()):
    ''' Used to get a player account by id.
    
    Args:
        - JWT token(Header)
    
    Returns:
        - player account
    '''

    return player_service.find_player_account_by_id(id, x_token)
    

@players_router.delete('/id', description='Delete player:')
def delete_player_by_id(id:int = Query(..., description='Enter id of the player you want to delete:'), x_token: str = Header()):
    ''' Used to delete a player account by id.
    
    Args:
        - JWT token(Header)
    
    Returns:
        - deleted player
    '''

    return player_service.delete_player_account_by_id(id, x_token)