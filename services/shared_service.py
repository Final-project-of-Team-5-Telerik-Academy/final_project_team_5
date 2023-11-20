from data.database import read_query, insert_query
from my_models.model_admin_requests import AdminRequests


def id_exists(id: int, table_name: str) -> bool:
    ''' Used to check if the id exists in the GIVEN table(users, players, matches, tournaments, admin_requests) in the database.

    Returns:
        - True/False
    '''

    return any(
        read_query(
            f'SELECT id FROM {table_name} WHERE id = ?',
            (id,)))


def id_exists_requests(id: int):
    ''' Used to check if the id exists in admin_requests in the database.

    Returns:
        - status from admin_requests
    '''

    data = read_query(
        f'SELECT id, type_of_request, players_id, users_id, status FROM admin_requests WHERE id = ?',
        (id,))

    result = next((AdminRequests.from_query_result(*row, ) for row in data), None)

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


def delete_request(id: int):
    ''' Used for deleting requests from the database.'''

    insert_query('''DELETE FROM admin_requests WHERE id = ?''',
                 (id,))


def get_creator_full_name(table: str, title: str):
    # get creator full name from tables: Matches and Tournaments
    creator_name = read_query(f'SELECT users_creator_id FROM {table} WHERE title = ?', (title, ))
    return creator_name if creator_name else None
