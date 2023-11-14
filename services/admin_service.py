from data.database import read_query, insert_query, update_query
from my_models.model_user import User
from my_models.model_player import Player
from my_models.model_user import User

from fastapi import HTTPException
from services import util_service

_SEPARATOR = ';'


def find_all_users() -> User | None:
    ''' Search in the database and creates a list of all users. Only admins can view a list of all users.
     
    Returns:
        - a list of all users(id, full_name, email, gender, role, players_id)
    '''

    data = read_query('SELECT id, full_name, email, password, gender, role, players_id FROM users')

    result = (User.from_query_result_no_password(*row) for row in data)

    return result


def find_user_by_role(role) -> User | None:
    ''' Search in the database and creates a list of all users with the given role. Only admins can view the list.
     
    Returns:
        - a list of all admins(id, full_name, email, gender, role, players_id)
    '''

    data = read_query('SELECT id, full_name, email, password, gender, role, players_id FROM users WHERE role = ?',
                      (role,))

    result = (User.from_query_result_no_password(*row) for row in data)

    return result


def find_user_by_id(id: int) -> User | None:
    ''' Search through users.id the whole information about the account in the data. Only admins can search for them.
     
    Args:
        - id: int 
        
    Returns:
        - all the necessary information about the user (id, full_name, email, gender, role, players_id)
    '''

    data = read_query(
        'SELECT id, full_name, email, password, gender, role, players_id FROM users WHERE id = ?',
        (id,))

    return next((User.from_query_result_no_password(*row) for row in data), None)


def edit_user_role(old_user: User, new_role: str):
    ''' Used for editing by an admin a role of a user in the database.'''
    
    edited_user = User(
        id=old_user.id,
        full_name=old_user.full_name,
        email=old_user.email,
        password=old_user.password,
        gender=old_user.gender,
        role=new_role,
        players_id=old_user.players_id
    )

    update_query('''UPDATE users SET role = ? WHERE id = ?''',
                (edited_user.role, edited_user.id))

    return {"User's role is updated."}


def edit_user_players_id(old_user: User, players_id: int):
    ''' Used by an admin for adding a players_id in user in the database.'''
    
    edited_user = User(
        id=old_user.id,
        full_name=old_user.full_name,
        email=old_user.email,
        password=old_user.password,
        gender=old_user.gender,
        role=old_user.role,
        players_id=players_id
    )

    update_query('''UPDATE users SET players_id = ? WHERE id = ?''',
                (edited_user.players_id, edited_user.id))

    return {'User is successfully connectected to player.'}


def delete_user(id: int):
    ''' Used for deleting the user from the database.'''

    insert_query('''DELETE FROM users WHERE id = ?''',
                 (id,))


def delete_players_id_from_user(id: int):
    ''' Used for deleting the players_id from user in the database.'''

    insert_query('''DELETE players_id FROM users WHERE id = ?''',
                 (id,))

# --------------------------------------------------------------------------------------

def create_player(full_name: str, country: str, sport_club: str) -> Player:
    ''' Used for creating a new player.

    Args:
        - full_name: Full name of the player
        - country: Country of the player
        - sport_club: Sport club of the player

    Returns:
        - Created player information
    '''

    if util_service.full_name_exists(full_name, 'players'):
        raise HTTPException(status_code=400, detail=f'The full name: {full_name} is already taken!')


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
        statistic_matches_id=statistics_matches_id
    )