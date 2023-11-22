from fastapi import APIRouter, Header, Query, Form
from services import shared_service
from services import admin_service
from services import player_service
from services import user_service
from services import email_service
from authentication.authenticator import get_user_or_raise_401
from my_models.model_user import User
from fastapi.responses import JSONResponse


admins_router = APIRouter(prefix='/admins', tags={'Admins'})


@admins_router.get('/users', description='View users:')
def user_info(id: int = Query(default=None, description="Enter ID of user:"), 
              role: str = Query(default=None, description="Enter role of user: spectator/player/director/admin"),
              x_token: str = Header(default=None)
              ):
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
    
    if id != None and role != None:
            return JSONResponse(status_code=400, content='You are allowed to search users either by id or by role, but not by both at the same time.')
    
    elif id != None and role == None:
        if not shared_service.id_exists(id, 'users'):
            return JSONResponse(status_code=404, content=f'User with id: {id} does not exist.')
        else:
            return admin_service.find_user_by_id(id)
        
    elif role != None and id == None:
        if role != 'spectator' and role != 'player' and role != 'director' and role != 'admin':
            return JSONResponse(status_code=400, content=f"Unrecognized role: '{role}'")
        else:
            return admin_service.find_user_by_role(role)
        
    return admin_service.find_all_users()


@admins_router.put('/users', description="Edit user's account:")
def edit_users(id: int = Query(..., description='Enter ID of user:'),
                    new_role: str = Form(..., description='Choose your role:',example='spectator', enum = ['spectator', 'player', 'director']),
                    command: str = Form(..., description='Choose a between:',example='promotion', enum = ['promotion', 'demotion', 'connection']),
                    players_id: int = Query(default=None, description='Enter ID of player:'),
                    x_token: str = Header(default=None)
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

    if x_token == None:
        return JSONResponse(status_code=401, content="You must be logged in and be an admin to be able to edit accounts.")
    
    user = get_user_or_raise_401(x_token)

    if not User.is_admin(user):
        return JSONResponse(status_code=401, content='Only admins can edit accounts.')

    if not shared_service.id_exists(id, 'users'):
        return JSONResponse(status_code=404, content=f'User with id: {id} does not exist.')
    
    old_user = admin_service.find_user_by_id(id)

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
        
        if shared_service.players_id_exists(players_id, 'users'):
            return JSONResponse(status_code=400, content=f'Player with id: {players_id} is already connected to a user.')
        
        if old_user.players_id == players_id:
            return JSONResponse(status_code=400, content=f'You are already connected to player with id: {players_id}.')
        
        admin_service.edit_user_players_id(old_user, players_id)
        
        is_connected = 1
        player_service.edit_is_connected_in_player(is_connected, players_id)
        
        new_role = 'player'
        admin_service.edit_user_role(old_user, new_role)

        email_type = 'link_profile_approved'
        email_service.send_email(old_user.email, email_type)
        
        if shared_service.user_connection_request_exists(old_user.id):
            request_status = 'finished'
            type_of_request = 'connection'
            admin_service.edit_requests_connection_status(request_status, players_id, type_of_request, id)
            return f"User's account is linked with players_id: {players_id}, user's role is updated to: '{new_role}' and the status of the request is updated to 'finished'."

        return f"User's account is linked with players_id: {players_id} and user's role is updated to: '{new_role}'."

    # Change role of user: promotion and demotion
    elif new_role != None and players_id == None and command != None:
        
        # demote from 'director' to 'player'
        if new_role == 'player' and command == 'demotion':
            if User.is_player(old_user):
                return JSONResponse(status_code=400, content="User's role is already a 'player'.")
            elif User.is_director(old_user):
                admin_service.edit_user_role(old_user, new_role)
                
                is_active = 0
                is_connected = 1
                player_service.edit_is_active_in_player(is_active, old_user.full_name, is_connected)

                return {f"User's role is demoted to '{new_role}' and player's account is activated."}

        # demote from 'director' to 'spectator'   
        elif new_role == 'spectator' and command == 'demotion':
            if User.is_spectator(old_user):
                return JSONResponse(status_code=400, content="User's role is already a 'spectator'.")
            elif User.is_director(old_user):
                admin_service.edit_user_role(old_user, new_role)
                
                is_connected = 0
                player_service.edit_is_connected_in_player(is_connected, old_user.players_id)

                admin_service.delete_players_id_from_user(old_user.id)

                return {f"User's role is demoted to '{new_role}' and player's account is disconnected from the user."}
        
        # promote from 'player' to 'director'
        elif new_role == 'director' and command == 'promotion':
            if User.is_director(old_user):
                return JSONResponse(status_code=400, content="User's role is already 'director'.")
            elif User.is_spectator(old_user):
                return JSONResponse(status_code=400, content="User's role cannot be changed from 'spectator' to 'director'.")
            elif User.is_player(old_user):
                admin_service.edit_user_role(old_user, new_role)
                
                if shared_service.user_promotion_request_exists(old_user.id):
                    request_status = 'finished'
                    type_of_request = 'promotion'
                    admin_service.edit_requests_promotion_status(request_status, type_of_request, id)
                
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


@admins_router.delete('/users', description="Delete user's account:")
def delete_user(id: int = Query(..., description='Enter ID of the user you want to delete:'), 
                x_token: str = Header(default=None)
                ):
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
    
    if not shared_service.id_exists(id, 'users'):
        return JSONResponse(status_code=404, content=f'User with id: {id} does not exist.')
    
    admin_service.delete_user(id)
        
    return {'User is deleted.'}
