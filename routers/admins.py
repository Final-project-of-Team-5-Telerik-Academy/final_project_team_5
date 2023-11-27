from fastapi import APIRouter, Header, Query, Form
from services import admin_service


admins_router = APIRouter(prefix='/admins', tags={'Admins'})


@admins_router.get('/users', description='View users:')
def user_info(id: int = Query(default=None, description="Enter ID of user:"), 
              role: str = Query(default=None, description="Enter role of user: spectator/player/director/admin"),
              x_token: str = Header()):
    ''' Used for admins to see data information about a user(by id), list of users(by role) or all registered users.
    
    Args:
        - user.id: int(Query)
        - role: str(Query)
        - JWT token
    
    Returns:
        - user(id, full_name, email, gender, role and players_id)
    '''

    return admin_service.get_user_info_by_id_or_role(id, role, x_token)


@admins_router.put('/users', description="Edit user's account:")
def edit_users(id: int = Query(..., description='Enter ID of user:'),
                    new_role: str = Form(..., description='Choose your role:',example='spectator', enum = ['spectator', 'player', 'director']),
                    command: str = Form(..., description='Choose a between:',example='promotion', enum = ['promotion', 'demotion', 'connection']),
                    players_id: int = Query(default=None, description='Enter ID of player:'),
                    x_token: str = Header()
                    ):
    ''' Used for editing a user's role through user.id or adding players_id into user. Only admins can use it.

    Args:
        - user.id: int(Query)
        - new_role: str(Query)
        - players_id: int(Query)
        - JWT token
    
    Returns:
        - Edited user
    '''

    return admin_service.edit_user_by_id(id, new_role, command, players_id, x_token)


@admins_router.delete('/users', description="Delete user's account:")
def delete_user(id: int = Query(..., description='Enter ID of the user you want to delete:'), 
                x_token: str = Header()):
    ''' Used for deleting a user through user.id. Only admins can delete it.

    Args:
        - user.id: int(URL link)
        - JWT token
    
    Returns:
        - Deleted user
    '''

    return admin_service.delete_users_account(id, x_token)


@admins_router.post('/blocked/players', description='Please enter the id of the player you want to block:')
def blocked_players(players_id: int = Query(..., description='Enter ID of the player you want to block:'),
                 ban_status: str = Form(..., description='Choose ban status:',example='temporary', enum = ['temporary', 'permanent']),
                 x_token: str = Header()):
    ''' Used for blockin players. Only admins can delete it.

    Args:
        - players_id: int(URL link)
        - ban_status: str
        - JWT token
    
    Returns:
        - Blocked player
    '''
    
    return admin_service.block_player_by_id(players_id, ban_status, x_token)


@admins_router.get('/blocked/players', description= 'Show all blocked players:')
def find_all_blocked_players(x_token: str = Header()):
    ''' Used for finding all blocked players.

    Args:
        - JWT token
    
    Returns:
        - list of blocked players
    '''

    return admin_service.find_all_blocked_players(x_token)


@admins_router.delete('/blocked/players', description="Remove player's block:")
def remove_players_block(players_id: int = Query(..., description='Enter ID of the blocked player you want to unblock:'), 
                x_token: str = Header()):
    ''' Used for deleting a player from the blocked_players database. Only admins can do it.

    Returns:
        - Player is unblocked.
    '''

    return admin_service.remove_block_of_player(players_id, x_token)
