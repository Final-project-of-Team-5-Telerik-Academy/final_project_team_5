from data.database import read_query, insert_query
from my_models.model_admin_requests import AdminRequests
from my_models.model_director_requests import DirectorRequests
from fastapi.responses import JSONResponse
import re

def id_exists(id: int, table_name: str) -> bool:
    ''' Used to check if the id exists in the GIVEN table(users, players, matches, tournaments, admin_requests, director_requests) in the database.

    Returns:
        - True/False
    '''

    return any(
        read_query(
            f'SELECT id FROM {table_name} WHERE id = ?',
            (id,)))


def id_exists_admin_requests(id: int):
    ''' Used to check if the id exists in admin_requests in the database.

    Returns:
        - status from admin_requests
    '''

    data = read_query(
        f'SELECT id, type_of_request, players_id, users_id, status FROM admin_requests WHERE id = ?',
        (id,))

    result = next((AdminRequests.from_query_result(*row, ) for row in data), None)

    return result


def id_exists_admin_requests_full_info(id: int):
    ''' Used to check if the id exists in admin_requests in the database.

    Returns:
        - admin_request
    '''

    data = read_query(
        f'SELECT id, type_of_request, players_id, users_id, status FROM admin_requests WHERE id = ?',
        (id,))

    result = next((AdminRequests.from_query_result(*row, ) for row in data), None)

    return result


def id_exists_director_requests(id: int):
    ''' Used to check if the id exists in director_requests in the database.

    Returns:
        - status from director_requests
    '''

    data = read_query(
        f'SELECT id, full_name, country, sports_club, users_id, status FROM director_requests WHERE id = ?',
        (id,))

    result = next((DirectorRequests.from_query_result(*row, ) for row in data), None)

    return result


def user_connection_request_exists(user_id: int):
    ''' Used to check if the id exists in admin_requests in the database.

    Returns:
        - Status from admin_requests if the user_id exists, None otherwise.
    '''

    status = 'pending'
    type_of_request = 'connection'

    result = read_query(
        'SELECT id, type_of_request, players_id, users_id, status FROM admin_requests WHERE users_id = ? and status = ? and type_of_request = ?',
        (user_id, status, type_of_request)
    )

    result = next((AdminRequests.from_query_result(*row, ) for row in result), None)

    return result
        

def user_promotion_request_exists(user_id: int):
    ''' Used to check if the id exists in admin_requests in the database.

    Returns:
        - Status from admin_requests if the user_id exists, None otherwise.
    '''

    status = 'pending'
    type_of_request = 'promotion'

    result = read_query(
        'SELECT id, type_of_request, players_id, users_id, status FROM admin_requests WHERE users_id = ? and status = ? and type_of_request = ?',
        (user_id, status, type_of_request)
    )

    result = next((AdminRequests.from_query_result(*row, ) for row in result), None)

    return result


def director_request_exists(user_id: int):
    ''' Used to check if the id exists in admin_requests in the database.

    Returns:
        - Status from admin_requests if the user_id exists, None otherwise.
    '''

    status = 'pending'

    result = read_query(
        'SELECT id, full_name, country, sports_club, users_id, status FROM director_requests WHERE users_id = ? and status = ?',
        (user_id, status)
    )

    result = next((DirectorRequests.from_query_result(*row, ) for row in result), None)

    return result


def players_id_exists(players_id: int, table_name: str) -> bool:
    ''' Used to check if the players_id is already connected to another user in the database.'''

    return any(
        read_query(
            f'SELECT players_id FROM {table_name} WHERE players_id = ?',
            (players_id,)))


def email_exists(email: str) -> bool:
    ''' Used to check if the email exists in users table in the database.'''

    data = read_query(
        'SELECT email FROM users WHERE email = ?',
        (email,)
    )

    return bool(data)


def full_name_exists(full_name: str, table_name: str) -> bool:
    ''' Used to check if the full_name exists in the GIVEN table(users or players) in the database.'''

    return any(
        read_query(
            f'SELECT full_name FROM {table_name} WHERE full_name = ?',
            (full_name,)))


def delete_admin_request(id: int):
    ''' Used for deleting requests from the database.'''

    insert_query('''DELETE FROM admin_requests WHERE id = ?''',
                 (id,))
    

def delete_director_request(id: int):
    ''' Used for deleting director requests from the database.'''

    insert_query('''DELETE FROM director_requests WHERE id = ?''',
                 (id,))


def get_creator_full_name(table: str, title: str):
    # get creator full name from tables: Matches and Tournaments
    creator_name = read_query(f'SELECT users_creator_id FROM {table} WHERE title = ?', (title, ))
    return creator_name if creator_name else None


def id_of_player_exists(id: int) -> bool:
    ''' Used to check if the id is already connected to another user in the database.'''

    return any(
        read_query(
            f'SELECT id FROM players WHERE id = ?',
            (id,)))

def id_of_banned_player_exists(players_id: int) -> bool:
    ''' Used to check if the players_id is already in the database.'''

    return any(
        read_query(
            f'SELECT id FROM banned_players WHERE players_id = ?',
            (players_id,)))


def check_date_format(date: str):
# check format is correct    alternative: ^(0?[1-9]|[12][0-9]|3[01])[\/\-](0?[1-9]|1[012])[\/\-]\d{4}$
    pattern = re.compile(r'^\d{4}[\/\-](0?[1-9]|1[012])[\/\-](0?[1-9]|[12][0-9]|3[01])$')
    if not pattern.match(date):
        return JSONResponse(status_code=400, content="The date must be in format 'yyyy-m-d' (2023-3-15)")