from fastapi import APIRouter, Header, Query
from services import util_service
from services import admin_service
from authentication.authenticator import get_user_or_raise_401
from my_models.model_user import User
from fastapi.responses import JSONResponse


admins_router = APIRouter(prefix='/admins', tags={'Everything available for Admins.'})


@admins_router.get('/info/')
def user_info(id: int = Query(..., description="ID of the user."), 
              x_token: str = Header(default=None)
              ):
    ''' Used for admins to see data information about a user.
    
    Args:
        - user.id: int(URL link)
        - JWT token
    
    Returns:
        - user(id, username, role)
    '''

    if x_token == None:
        return JSONResponse(status_code=401, content='You must be logged in and be an admin to be able to review accounts.')
    
    user = get_user_or_raise_401(x_token)
    
    if not User.is_admin(user):
        return JSONResponse(status_code=401, content='Only admins can review accounts.')
    
    if not util_service.id_exists(id, 'users'):
        return JSONResponse(status_code=404, content=f'User with id: {id} does not exist.')
    
    return admin_service.find_user_by_id(id)


@admins_router.put('/edit')
def edit_users_role(id: int = Query(..., description="ID of the user."),
                    new_role: str = Query(..., description="New role of the user."), 
                    x_token: str = Header(default=None)
                    ):
    ''' Used for editing a user's role through user.id. Only admins can edit it.

    Args:
        - user.id: int(URL link)
        - JWT token
    
    Returns:
        - Edited user
    '''

    if x_token == None:
        return JSONResponse(status_code=401, content="You must be logged in and be an admin to be able to edit user's role.")
    
    user = get_user_or_raise_401(x_token)

    if not User.is_admin(user):
        return JSONResponse(status_code=401, content='Only admins can edit roles.')

    if new_role != 'spectator' and new_role != 'director':
        return JSONResponse(status_code=404, content="You can only switch to 'spectator' or 'director' role.")
    
    if not util_service.id_exists(id, 'users'):
        return JSONResponse(status_code=404, content=f'User with id: {id} does not exist.')
    
    old_user = admin_service.find_user_by_id(id)

    if new_role == 'spectator' and old_user.role == 'spectator':
        return JSONResponse(status_code=400, content="User's role is already 'spectator'.")
    if new_role == 'director' and old_user.role == 'director':
        return JSONResponse(status_code=400, content="User's role is already 'director'.")

    return admin_service.edit_user(old_user, new_role)


@admins_router.delete('/delete')
def delete_user(id: int = Query(..., description="ID of the user you want to delete."), 
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
        return JSONResponse(status_code=401, content='You must be admin to be able to delete a user.')
    
    if not util_service.id_exists(id, 'users'):
        return JSONResponse(status_code=404, content=f'User with id: {id} does not exist.')
    
    admin_service.delete_user(id)
        
    return {'User is deleted.'}

