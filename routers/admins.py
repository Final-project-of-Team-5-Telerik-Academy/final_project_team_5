from fastapi import APIRouter, Header, Query
from services import util_service
from services import admin_service
from authentication.authenticator import get_user_or_raise_401, find_by_id
from my_models.model_user import User
from fastapi.responses import JSONResponse
from services import util_service 

admins_router = APIRouter(prefix='/admins', tags={'Everything available for Admins.'})


@admins_router.get('/info/users')
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
        if not util_service.id_exists(id, 'users'):
            return JSONResponse(status_code=404, content=f'User with id: {id} does not exist.')
        else:
            return admin_service.find_user_by_id(id)
        
    elif role != None and id == None:
        if role != 'spectator' and role != 'player' and role != 'director' and role != 'admin':
            return JSONResponse(status_code=400, content=f"Unrecognized role: '{role}'")
        else:
            return admin_service.find_user_by_role(role)
        
    return admin_service.find_all_users()


@admins_router.put('/edit')
def edit_users_role(id: int = Query(..., description='Enter ID of user:'),
                    new_role: str = Query(default=None, description='Enter new role of user:'),
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

    if not util_service.id_exists(id, 'users'):
        return JSONResponse(status_code=404, content=f'User with id: {id} does not exist.')
    
    old_user = admin_service.find_user_by_id(id)

    # both are None:
    if new_role == None and players_id == None:
        return JSONResponse(status_code=400, content="You must enter either a new_role or a players_id.")

    # both are != None:
    elif new_role != None and players_id != None:
        return JSONResponse(status_code=401, content="You are not allowed to change the role and to add players_id in the same time.")
    
    # connect user's account with player's account:
    elif new_role == None and players_id != None:
        if not util_service.id_exists(players_id, 'players'):
            return JSONResponse(status_code=404, content=f'Player with id: {players_id} does not exist.')
        
        # !!! да се тества след като се добави Player модел !!!
        if util_service.players_id_exists(players_id, 'users'):
            return JSONResponse(status_code=400, content=f'Player with id: {players_id} is already connected to a user.')
        
        new_role = 'player'
        
        admin_service.edit_user_players_id(old_user, players_id)
        admin_service.edit_user_role(old_user, new_role)
        
        return f"User's account is linked with players_id: {players_id} and user's role is updated to: {new_role}."

    # Change role of user: promotion and demotion
    elif new_role != None and players_id == None:
        if new_role == 'player':
            if User.is_player(user):
                return JSONResponse(status_code=400, content=f"User's role is already {new_role} and the user is connected to player's account.")
            return JSONResponse(status_code=400, content="You can only change the role to 'player' when connecting user's account to player's account.")
        
        if new_role != 'spectator' and new_role != 'director':
            return JSONResponse(status_code=400, content="You can only switch the role to 'spectator' or 'director'.")
        
        # demote from 'director' to 'spectator'
        elif new_role == 'spectator':
            if User.is_spectator(old_user):
                return JSONResponse(status_code=400, content="User's role is already 'spectator'.")
            
            # !!! да се тества след като се добави Player модел !!!
            # disconnect user's account from player's acount and demote to 'spectator' role
            # elif User.is_player(old_user):
            #     admin_service.edit_user_role(old_user, new_role)
            #     admin_service.delete_players_id_from_user(id)

            #     return {f"User's role is demoted to {new_role} and user's account is disconnected from player's account."}
            
            admin_service.edit_user_role(old_user, new_role)
            return {f"User's role is demoted from 'director' to '{new_role}'."}
            
        
        # !!! да се добави първо викане на функция за пенсиониране на player и тогава да се откоментира !!!
        # promote from 'player' to 'director'
        # elif new_role == 'director' and User.is_player(user.id):
        #     admin_service.edit_user_role(old_user, new_role)
        #     # да се добави викане на функция за пенсиониране на player!
        #     return {f"User's role is promoted to {new_role} and linked player's account is retired."}
        
        # promote from 'spectator' to 'director'
        elif new_role == 'director':
            if User.is_director(old_user):
                return JSONResponse(status_code=400, content="User's role is already 'director'.")
            admin_service.edit_user_role(old_user, new_role)
            return {f"User's role is promoted to '{new_role}'."}


@admins_router.delete('/delete')
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
        return JSONResponse(status_code=401, content='You must be logged in and be an admin to be able to delete a user.')    
    
    user = get_user_or_raise_401(x_token)
    
    if not User.is_admin(user):
        return JSONResponse(status_code=401, content='You must be an admin to be able to delete a user.')
    
    if not util_service.id_exists(id, 'users'):
        return JSONResponse(status_code=404, content=f'User with id: {id} does not exist.')
    
    admin_service.delete_user(id)
        
    return {'User is deleted.'}


# __________________________________________________________________________________________


@admins_router.post('/create_player', description='Create a new player')
def create_player(full_name: str = Query(..., description='Enter full name of player:'),
                  country: str = Query(..., description='Enter country of player:'),
                  sport_club: str = Query(..., description='Enter sport club of player:'),
                  x_token: str = Header(default=None)):
    ''' Used for creating a new player.

    Args:
        - full_name: Full name of the player
        - country: Country of the player
        - sport_club: Sport club of the player
        - x_token: JWT token

    Returns:
        - Created player information
    '''
    if x_token == None:
        return JSONResponse(status_code=401, content='You must be logged in and be an admin to be able to create a player.')    
    
    user = get_user_or_raise_401(x_token)
    
    if not User.is_admin(user):
        return JSONResponse(status_code=401, content='You must be an admin to be able to create a player.')
    
    created_player = admin_service.create_player(full_name, country, sport_club)

    return created_player

   