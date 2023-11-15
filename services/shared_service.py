from data.database import read_query, insert_query
from my_models.model_player import Player
from fastapi.responses import JSONResponse


def id_exists(id: int, table_name: str) -> bool:
    ''' Used to check if the id exists in the GIVEN table(users, players, matches, tournaments) in the database.'''

    return any(
        read_query(
            f'SELECT id FROM {table_name} WHERE id = ?',
            (id,)))


def players_id_exists(players_id: int, table_name: str) -> bool:
    ''' Used to check if the players_id is already connected to another user in the database.'''

    return any(
        read_query(
            f'SELECT players_id FROM {table_name} WHERE players_id = ?',
            (players_id,)))


def email_exists(email:str) -> bool:
    ''' Used to check if the email exists in users table in the database.'''

    data = read_query(
        'SELECT email FROM users WHERE email = ?',
        (email,)
    )

    return bool(data)


def full_name_exists(full_name:str, table_name:str) -> bool:
    ''' Used to check if the full_name exists in the GIVEN table(users or players) in the database.'''

    return any(
        read_query(
            f'SELECT full_name FROM {table_name} WHERE full_name = ?',
            (full_name,)))


def create_player(full_name: str, country: str, sport_club: str) -> Player:
    ''' Used for creating a new player.

    Args:
        - full_name: str
        - country: str
        - sport_club: str

    Returns:
        - Created player information
    '''

    if full_name_exists(full_name, 'players'):
        return JSONResponse(status_code=400, content=f'The full name: {full_name} is already taken!')

    statistics_matches_id = None
    audience_vote = 0
    points = 0
    titles = 0
    wins = 0
    losses = 0
    money_prize = 0
    is_injured = 0
    is_active = 1
    
    generated_id = insert_query(
        'INSERT INTO players(full_name, country, sport_club, audience_vote, points, titles, wins, losses, money_prize, is_injured, is_active, statistics_matches_id) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)',
        (full_name, country, sport_club, audience_vote, points, titles, wins, losses, money_prize, is_injured, is_active, statistics_matches_id)  
    )

    return Player(
        id=generated_id,
        full_name=full_name,
        country=country,
        sport_club=sport_club,
        audience_vote=audience_vote,
        points=points,
        titles=titles,
        wins=wins,
        losses=losses,
        money_prize=money_prize,
        is_injured=is_injured,
        is_active=is_active,
        statistics_matches_id=statistics_matches_id
    )


def find_all_players() -> Player | None:
    ''' Search in the database and creates a list of all players. 
    Returns:
        - a list of all players(id, full_name, country, sport_club, audience_vote, points, titles, wins, losses, money_prize, is_injured, is_active, statistics_matches_id)
    '''

    data = read_query('SELECT id, full_name, country, sport_club, audience_vote, points, titles, wins, losses, money_prize, is_injured, is_active, statistics_matches_id FROM players')

    result = (Player.from_query_result(*row) for row in data)

    return result