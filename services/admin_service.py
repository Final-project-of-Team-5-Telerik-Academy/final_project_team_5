from data.database import read_query, insert_query, update_query
from my_models.model_user import User
from my_models.model_admin_requests import AdminRequests
from fastapi.responses import JSONResponse
from authentication.authenticator import get_user_or_raise_401
from services import shared_service
from services import player_service
from services import email_service
from my_models.model_blocked_players import BlockedPlayers


_SEPARATOR = ';'


def find_all_users() -> User | None:
    ''' Search in the database and creates a list of all users. Only admins can view a list of all users.
     
    Returns:
        - a list of all users(id, full_name, email, gender, role, players_id), without password, is_verified, verification_code
    '''

    data = read_query('SELECT id, full_name, email, password, gender, role, players_id, is_verified, verification_code FROM users')

    result = (User.from_query_result_no_password(*row) for row in data)

    return result


def find_user_by_role(role) -> User | None:
    ''' Search in the database and creates a list of all users with the given role. Only admins can view the list.
     
    Returns:
        - a list of all admins(id, full_name, email, gender, role, players_id), without password, is_verified, verification_code
    '''

    data = read_query('SELECT id, full_name, email, password, gender, role, players_id, is_verified, verification_code FROM users WHERE role = ?',
                      (role,))

    result = (User.from_query_result_no_password(*row) for row in data)

    return result


def find_user_by_id(id: int) -> User | None:
    ''' Search through users.id the whole information about the account in the data. Only admins can search for them.
     
    Args:
        - id: int 
        
    Returns:
        - all the necessary information about the user (id, full_name, email, gender, role, players_id) without password, is_verified, verification_code
    '''

    data = read_query(
        'SELECT id, full_name, email, password, gender, role, players_id, is_verified, verification_code FROM users WHERE id = ?',
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


def get_all_admin_requests() -> AdminRequests | None:
    ''' Used to take all requests in admin_requests in the database.
    
    Returns:
        - list of requests from users
    '''

    data = read_query('SELECT id, type_of_request, players_id, users_id, status FROM admin_requests')
    
    return (AdminRequests.from_query_result(*row) for row in data)


def get_admin_request_by_id(id: int):
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


def delete_users_account(id: int, x_token: str):
    ''' Used for deleting a user through user.id. Only admins can delete it.

    Args:
        - user.id: int(URL link)
        - JWT token
    
    Returns:
        - Deleted user
    '''

    if x_token == None:
        return JSONResponse(status_code=401, content='You must be logged in and be an admin to be able to delete an user.')    
    
    user = get_user_or_raise_401(x_token)
    
    if not User.is_admin(user):
        return JSONResponse(status_code=401, content='You must be an admin to be able to delete an user.')
    
    elif not shared_service.id_exists(id, 'users'):
        return JSONResponse(status_code=404, content=f'User with id: {id} does not exist.')
    
    delete_user(id)
        
    return {'User is deleted.'}


def get_user_info_by_id_or_role(id: int, role: str, x_token: str):
    ''' Used for admins to see data information about a user(by id), list of users(by role) or all registered users.
    
    Args:
        - user.id: int(Query)
        - role: str(Query)
        - JWT token
    
    Returns:
        - user(id, full_name, email, gender, role and players_id)
    '''

    if x_token == None:
        return JSONResponse(status_code=401, content='You must be logged in and be an admin to be able to review accounts.')
    
    user = get_user_or_raise_401(x_token)
    
    if not User.is_admin(user):
        return JSONResponse(status_code=401, content='Only admins can review accounts.')
    
    elif id != None and role != None:
            return JSONResponse(status_code=400, content='You are allowed to search users either by id or by role, but not by both at the same time.')
    
    elif id != None and role == None:
        if not shared_service.id_exists(id, 'users'):
            return JSONResponse(status_code=404, content=f'User with id: {id} does not exist.')
        else:
            return find_user_by_id(id)
        
    elif role != None and id == None:
        if role != 'spectator' and role != 'player' and role != 'director' and role != 'admin':
            return JSONResponse(status_code=400, content=f"Unrecognized role: '{role}'")
        else:
            return find_user_by_role(role)
        
    return find_all_users()


def edit_user_by_id(id: int, new_role: str, command: str, players_id: int , x_token: str):
    ''' Used for editing a user's role through user.id or adding players_id into user. Only admins can use it.

    Args:
        - user.id: int(Query)
        - new_role: str(Query)
        - players_id: int(Query)
        - JWT token
    
    Returns:
        - Edited user
    '''

    if x_token == None:
        return JSONResponse(status_code=401, content="You must be logged in and be an admin to be able to edit accounts.")
    
    user = get_user_or_raise_401(x_token)

    if not User.is_admin(user):
        return JSONResponse(status_code=401, content='Only admins can edit accounts.')

    elif not shared_service.id_exists(id, 'users'):
        return JSONResponse(status_code=404, content=f'User with id: {id} does not exist.')
    
    old_user = find_user_by_id(id)

    # both are None:
    if new_role == None and players_id == None:
        return JSONResponse(status_code=400, content="You must enter either a new_role with a command or just a players_id.")

    # both are != None:
    elif new_role != None and players_id != None:
        return JSONResponse(status_code=401, content="You are not allowed to change the role and to add players_id at the same time.")
    
    # new_role != None and command is not correct:
    elif new_role != None and command == 'connection':
        return JSONResponse(status_code=401, content="To edit user's role you must choose between 'promotion' or 'demotion' command.")
    
    # players_id != None and command is not correct
    elif players_id != None and new_role == None and (command == 'demotion' or command == 'promotion' ):
        return JSONResponse(status_code=401, content="To connect user's account to his player's account you must enter 'connection' command.")
    
    # connect user's account with player's account:
    elif new_role == None and players_id != None and command == 'connection':
        if not shared_service.id_exists(players_id, 'players'):
            return JSONResponse(status_code=404, content=f'Player with id: {players_id} does not exist.')
        
        elif shared_service.players_id_exists(players_id, 'users'):
            return JSONResponse(status_code=400, content=f'Player with id: {players_id} is already connected to a user.')
        
        elif old_user.players_id == players_id:
            return JSONResponse(status_code=400, content=f'You are already connected to player with id: {players_id}.')
        
        edit_user_players_id(old_user, players_id)
        
        is_connected = 1
        player_service.edit_is_connected_in_player(is_connected, players_id)
        
        new_role = 'player'
        edit_user_role(old_user, new_role)

        email_type = 'link_profile_approved'
        email_service.send_email(old_user.email, email_type)
        
        if shared_service.user_connection_request_exists(old_user.id):
            request_status = 'finished'
            type_of_request = 'connection'
            edit_requests_connection_status(request_status, players_id, type_of_request, id)
            return f"User's account is linked with players_id: {players_id}, user's role is updated to: '{new_role}' and the status of the request is updated to 'finished'."

        return f"User's account is linked with players_id: {players_id} and user's role is updated to: '{new_role}'."

    # Change role of user: promotion and demotion
    elif new_role != None and players_id == None and command != None:
        
        # demote from 'director' to 'player'
        if new_role == 'player' and command == 'demotion':
            if User.is_player(old_user):
                return JSONResponse(status_code=400, content="User's role is already a 'player'.")
            elif User.is_director(old_user):
                edit_user_role(old_user, new_role)
                
                is_active = 0
                is_connected = 1
                player_service.edit_is_active_in_player(is_active, old_user.full_name, is_connected)

                return {f"User's role is demoted to '{new_role}' and player's account is activated."}

        # demote from 'director' to 'spectator'   
        elif new_role == 'spectator' and command == 'demotion':
            if User.is_spectator(old_user):
                return JSONResponse(status_code=400, content="User's role is already a 'spectator'.")
            elif User.is_director(old_user):
                edit_user_role(old_user, new_role)
                
                is_connected = 0
                player_service.edit_is_connected_in_player(is_connected, old_user.players_id)

                delete_players_id_from_user(old_user.id)

                return {f"User's role is demoted to '{new_role}' and player's account is disconnected from the user."}
        
        # promote from 'player' to 'director'
        elif new_role == 'director' and command == 'promotion':
            if User.is_director(old_user):
                return JSONResponse(status_code=400, content="User's role is already 'director'.")
            elif User.is_spectator(old_user):
                return JSONResponse(status_code=400, content="User's role cannot be changed from 'spectator' to 'director'.")
            elif User.is_player(old_user):
                edit_user_role(old_user, new_role)
                
                if shared_service.user_promotion_request_exists(old_user.id):
                    request_status = 'finished'
                    type_of_request = 'promotion'
                    edit_requests_promotion_status(request_status, type_of_request, id)
                
                is_active = 1
                is_connected = 1
                player_service.edit_is_active_in_player(is_active, old_user.full_name, is_connected)

                email_type = 'promotion_approved'
                email_service.send_email(old_user.email, email_type)
            
                return {f"User's role is promoted to '{new_role}' and the connected player's account is retired."}
            
        else:
            return JSONResponse(status_code=400, content="Unrecognized request.")
            
    else:
        return JSONResponse(status_code=400, content="Unrecognized request.")
    

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


def block_player_by_id(players_id: int, ban_status: str, x_token: str):
    ''' Used for blockin players. Only admins can delete it.

    Args:
        - players_id: int(URL link)
        - ban_status: str
        - JWT token
    
    Returns:
        - Blocked player
    '''
    
    if x_token == None:
        return JSONResponse(status_code=401, content='You must be logged in and be an admin to be able to block a player.')
    
    user = get_user_or_raise_401(x_token)
    
    if not User.is_admin(user):
        return JSONResponse(status_code=401, content='You must be an admin to be able to block a player.')
    
    if not shared_service.id_of_player_exists(players_id):
        return JSONResponse(status_code=404, content=f'Player with id: {players_id} does not exist.')
    
    if not shared_service.id_of_blocked_player_exists(players_id):
        insert_blocked_player(players_id, ban_status)
    else:
        return JSONResponse(status_code=404, content = f'Player with id: {players_id} already exists.')
    
    player_service.edit_is_active_in_player_by_id(players_id)

    return {'message': 'Player is blocked successfully.'}


def find_all_blocked_players(x_token: str):
    ''' Used for finding all blocked players.

    Args:
        - JWT token
    
    Returns:
        - list of blocked players
    '''

    if x_token == None:
        return JSONResponse(status_code=401, content='You must be logged in and be an admin to see the list of blocked players.')
    
    user = get_user_or_raise_401(x_token)
    
    if User.is_admin(user):
        list_of_players = get_all_blocked_players()
    else: 
        return JSONResponse(status_code=401, content='You must be an admin to see the list of blocked players.')

    return list_of_players


def remove_block_of_player(players_id: int, x_token: str):
    ''' Used for deleting a player from the blocked_players database. Only admins can do it.

    Returns:
        - Player is unblocked.
    '''

    if x_token == None:
        return JSONResponse(status_code=401, content='You must be logged in and be an admin to be able to unblock a player.')    
    
    user = get_user_or_raise_401(x_token)
    
    if not User.is_admin(user):
        return JSONResponse(status_code=401, content='You must be an admin to be able to unblock a player.')
    
    if not shared_service.id_of_blocked_player_exists(players_id):
        return JSONResponse(status_code=404, content=f"Player with id {players_id} is not blocked.")
    
    remove_blocked_player(players_id)
    player_service.back_is_active_in_player_by_id(players_id)
    
    return {'Message': 'Player is unblocked.'}