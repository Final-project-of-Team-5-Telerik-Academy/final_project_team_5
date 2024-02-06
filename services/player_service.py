from my_models.model_player import Player
from data.database import read_query, insert_query, update_query
from services.shared_service import full_name_exists
from fastapi.responses import JSONResponse
from authentication.authenticator import get_user_or_raise_401
from my_models.model_user import User
from services import user_service
from services import shared_service


def get_player_by_id(players_id: int) -> Player | None:

    data = read_query(
        'SELECT id, full_name, country, sports_club, is_active, is_connected, teams_id, banned_players_id FROM players WHERE id = ?',
        (players_id,)
        )
    
    if data is None:
        return JSONResponse(status_code=404, content=f'Player with ID: {players_id} does not exist.')
    
    result = next(Player.from_query_result(*row) for row in data)

    return result


def get_player_by_full_name(full_name: str) -> Player | None:

    data = read_query(
        'SELECT id, full_name, country, sports_club, is_active, is_connected, teams_id, banned_players_id FROM players WHERE full_name = ?',
        (full_name,)
        )
    
    if data is None:
        return JSONResponse(status_code=404, content=f'Player with full name: {full_name} does not exist.')

    return (Player.from_query_result(*row) for row in data)


def get_player_by_full_name_next(full_name: str) -> Player | None:

    data = read_query(
        'SELECT id, full_name, country, sports_club, is_active, is_connected, teams_id, banned_players_id FROM players WHERE full_name = ?',
        (full_name,)
        )

    return next((Player.from_query_result(*row) for row in data), None)


def get_all_players() -> Player | None:
    ''' Search in the database and creates a list of all players. 
    
    Returns:
        - a list of all players(id, full_name, country, sports_club, is_active, is_connected, teams_id, banned_players_id)
    '''

    data = read_query('SELECT id, full_name, country, sports_club, is_active, is_connected, teams_id, banned_players_id FROM players')

    if data is None:
        return JSONResponse(status_code=404, content='There are no registered players.')

    result = (Player.from_query_result(*row) for row in data)

    return result


def create_player(full_name: str, country: str, sports_club: str) -> Player:
    ''' Used for creating a new player.

    Args:
        - full_name: str
        - country: str
        - sports_club: str

    Returns:
        - Created player information
    '''

    if full_name_exists(full_name, 'players'):
        return JSONResponse(status_code=400, content=f'The full name: {full_name} is already taken!')

    is_active = 1
    is_connected = 0
    teams_id = None
    banned_players_id = None
    
    generated_id = insert_query(
        'INSERT INTO players(full_name, country, sports_club, is_active, is_connected, teams_id, banned_players_id) VALUES (?,?,?,?,?,?,?)',
        (full_name, country, sports_club, is_active, is_connected, teams_id, banned_players_id)  
    )

    return Player(
        id=generated_id,
        full_name=full_name,
        country=country,
        sports_club=sports_club,
        is_active=is_active,
        is_connected=is_connected,
        teams_id=teams_id,
        banned_players_id=banned_players_id
    )


def edit_is_connected_in_player(is_connected: int, id: int) -> Player:
    ''' Used for editing is_connected in a player.

    Returns:
        - Edited player information
    '''

    update_query('''UPDATE players SET is_connected = ? WHERE id = ?''',
                (is_connected, id))


def edit_is_active_in_player(is_active: int, full_name: str, is_connected: int) -> Player:
    ''' Used for editing is_active in a player.

    Returns:
        - Edited player information
    '''

    update_query('''UPDATE players SET is_active = ? WHERE full_name = ? and is_connected = ?''',
                (is_active, full_name, is_connected))
    

def delete_player(id: int):
    ''' Used for deleting the player from the database.'''
    
    new_players_id = None
    new_role = 'spectator'

    update_query('''UPDATE users SET role = ? WHERE players_id = ?''',
                (new_role, id))
    
    update_query('''UPDATE users SET players_id = ? WHERE players_id = ?''',
                (new_players_id, id))
    
    insert_query('''DELETE FROM players WHERE id = ?''',
                 (id,))
    
    
def edit_is_active_in_player_by_id(id: int) -> Player:
    ''' Used for editing is_active in a player.

    Returns:
        - Edited player information
    '''

    is_active = 0
    update_query('''UPDATE players SET is_active = ? WHERE id = ? ''',
                (is_active, id))
    
    
def back_is_active_in_player_by_id(id: int) -> Player:
    ''' Used for editing is_active in a player.

    Returns:
        - Edited player information
    '''
    is_active = 1
    update_query('''UPDATE players SET is_active = ? WHERE id = ? ''',
                (is_active, id))
    

def create_player_account(full_name: str, country: str, sports_club: str, x_token: str):
    ''' Used for creating a new player by a director or admin.

    Args:
        - full_name: str(Query)
        - country: str(Query)
        - sports_club: str(Query)
        - x_token: JWT token(Header)

    Returns:
        - Created player information
    '''
    
    user = get_user_or_raise_401(x_token)

    if User.is_director(user):
        created_player = create_player(full_name, country, sports_club)
    elif User.is_admin(user):
        created_player = create_player(full_name, country, sports_club)
    else:
        return JSONResponse(status_code=401, content='You must be an admin or a director to be able to create a player.')
    
    if user_service.director_request_exists(full_name):
            old_status = 'pending'
            new_status = 'finished'
            user_service.update_director_request_status(new_status, full_name, old_status)

    return created_player


def edit_player_account(full_name: str, country: str, sports_club: str, x_token: str):
    ''' Used for editing a new player by a director or admin.

    Args:
        - full_name: str(Query)
        - country: str(Query)
        - sports_club: str(Query)
        - x_token: JWT token(Header)

    Returns:
        - Edited player information
    '''
    
    user = get_user_or_raise_401(x_token)
    player = get_player_by_full_name_next(full_name)
    
    if player == None:
        return JSONResponse(status_code=404, content=f'Player with full name: {full_name} does not exist.')
    elif User.is_player(user):
        if user.players_id == player.id:
            edit_whole_player(full_name, country, sports_club)
        else:
            return JSONResponse(status_code=401, content='Unrecognized credentials.')
    elif User.is_director(user):
        if not Player.is_connected_account(player):
            edit_whole_player(full_name, country, sports_club)
        else:
            return JSONResponse(status_code=401, content='Unrecognized credentials.')
    elif User.is_admin(user):
        edit_whole_player(full_name, country, sports_club)
    else:
        return JSONResponse(status_code=401, content='Unrecognized credentials.')

    return {'Player is edited.'}


def edit_whole_player(full_name: str, country: str, sports_club: str) -> Player:
    ''' Used for editing a player.

    Returns:
        - Edited player information
    '''

    update_query('''UPDATE players SET country = ? WHERE full_name = ?''',
                (country, full_name))

    update_query('''UPDATE players SET sports_club = ? WHERE full_name = ?''',
                (sports_club, full_name))


def find_all_player_accounts():
    ''' Used to get all player accounts.
    
    Args:
        - JWT token(Header)
    
    Returns:
        - list of all player accounts
    '''

    list_of_players = get_all_players()

    return list_of_players


def find_player_account_by_id(id: int):
    ''' Used to get a player account by id.
    
    Args:
        - JWT token(Header)
    
    Returns:
        - player account
    '''

    if not shared_service.id_exists(id, 'players'):
            return JSONResponse(status_code=404, content=f'Player with id: {id} does not exist.')
    
    player = get_player_by_id(id)

    return player


def delete_player_account_by_id(id: int, x_token: str):
    ''' Used to delete a player account by id.
    
    Args:
        - JWT token(Header)
    
    Returns:
        - deleted player
    '''
    
    user = get_user_or_raise_401(x_token)
    
    if not User.is_admin(user):
        return JSONResponse(status_code=401, content='You must be an admin to be able to delete a player.')
    elif not shared_service.id_exists(id, 'players'):
        return JSONResponse(status_code=404, content=f'Player with id: {id} does not exist.')
    
    delete_player(id)
        
    return {'Player is deleted.'}
