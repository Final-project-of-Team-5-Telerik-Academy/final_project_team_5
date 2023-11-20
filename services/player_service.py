from my_models.model_player import Player
from data.database import read_query, insert_query, update_query
from services.shared_service import full_name_exists
from fastapi.responses import JSONResponse


def get_player_by_id(players_id: int) -> Player | None:

    data = read_query(
        'SELECT id, full_name, country, sports_club, is_active, is_connected, statistics_matches_id FROM players WHERE id = ?',
        (players_id,)
        )

    return next((Player.from_query_result(*row) for row in data), None)


def get_player_by_full_name(full_name: str) -> Player | None:

    data = read_query(
        'SELECT id, full_name, country, sports_club, is_active, is_connected, statistics_matches_id FROM players WHERE full_name = ?',
        (full_name,)
        )

    return next((Player.from_query_result(*row) for row in data), None)


def get_all_players() -> Player | None:
    ''' Search in the database and creates a list of all players. 
    
    Returns:
        - a list of all players(id, full_name, country, sports_club, is_active, is_connected, statistics_matches_id)
    '''

    data = read_query('SELECT id, full_name, country, sports_club, is_active, is_connected, statistics_matches_id FROM players')

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

    is_active = 0
    is_connected = 0
    statistics_matches_id = None
    
    generated_id = insert_query(
        'INSERT INTO players(full_name, country, sports_club, is_active, is_connected, statistics_matches_id) VALUES (?,?,?,?,?,?)',
        (full_name, country, sports_club, is_active, is_connected, statistics_matches_id)  
    )

    return Player(
        id=generated_id,
        full_name=full_name,
        country=country,
        sports_club=sports_club,
        is_active=is_active,
        is_connected=is_connected,
        statistics_matches_id=statistics_matches_id
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