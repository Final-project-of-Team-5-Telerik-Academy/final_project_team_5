from data.database import read_query, insert_query, update_query
from my_models.model_user import User
from my_models.model_admin_requests import AdminRequests
from my_models.model_blocked_players import BlockedPlayers, Status

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

    update_query('''UPDATE users SET players_id = NULL WHERE id = ?''',
                 (id,))


def get_all_requests() -> AdminRequests | None:
    ''' Used to take all requests in admin_requests in the database.
    
    Returns:
        - list of requests from users
    '''

    data = read_query('SELECT id, type_of_request, players_id, users_id, status FROM admin_requests')
    
    return (AdminRequests.from_query_result(*row) for row in data)


def get_requests_by_id(id: int):
    ''' Used to find a specific request in admin_requests in the database.
    
    Args:
        - id(int)
    Returns:
        - list of requests from users
    '''

    data = read_query('SELECT id, type_of_request, players_id, users_id, status FROM admin_requests WHERE id = ?',
                      (id,))
    
    return (AdminRequests.from_query_result(*row) for row in data)


def edit_requests_connection_status(request_status: str, players_id: int, type_of_request: str, id: int):
    ''' Used by an admin for editing the status in admin_requests in the database.'''

    update_query('''UPDATE admin_requests SET status = ? WHERE players_id = ? and type_of_request = ? and users_id = ?''',
                (request_status, players_id, type_of_request, id))


def edit_requests_promotion_status(request_status: str, type_of_request: str, id: int):
    ''' Used by an admin for editing the status in admin_requests in the database.'''

    update_query('''UPDATE admin_requests SET status = ? WHERE type_of_request = ? and users_id = ?''',
                (request_status, type_of_request, id))
    
 
def insert_blocked_player(players_id: int, ban_status: str) -> BlockedPlayers | None:
    generated_id = insert_query(
        'INSERT INTO blocked_players(players_id, ban_status) VALUES (?, ?)',
        (players_id, ban_status)
    )

    return BlockedPlayers(id=generated_id, players_id=players_id, ban_status=ban_status)


def get_all_blocked_players() -> BlockedPlayers | None:
    ''' Search in the database and creates a list of all blocked players. 
    
    Returns:
        - a list of all blocked players(id, players_id, ban_status)
    '''

    data = read_query('SELECT id, players_id, ban_status FROM blocked_players')

    result = (BlockedPlayers.from_query_result(*row) for row in data)

    return result


def remove_blocked_player(players_id: int):
    ''' Used for removing a blocked player from the database.'''

    insert_query('''DELETE FROM blocked_players WHERE players_id = ?''',
                 (players_id,))