from fastapi import APIRouter, Header, Query
from authentication.authenticator import get_user_or_raise_401
from my_models.model_team import Team
from my_models.model_user import User
from fastapi.responses import JSONResponse
from services import team_service
from services import shared_service


teams_router = APIRouter(prefix='/teams', tags={'Teams'})


@teams_router.post('/', description='Create a new team:')
def create_team(team_name: str = Query(..., description='Enter full name of team:'),
                  number_of_players: int = Query(..., description='Enter number of players:'),
                  x_token: str = Header(default=None)):
    ''' Used for creating a new team by a director or admin.

    Args:
        - team_name: str(Query)
        - number_of_players: int(Query)
        - x_token: JWT token(Header)

    Returns:
        - Created team information
    '''

    if x_token == None:
        return JSONResponse(status_code=401, content='You must be logged in and be an admin or a director to be able to create a player.')    
    
    user = get_user_or_raise_401(x_token)

    if User.is_director(user):
        created_team = team_service.create_team(team_name, number_of_players, user.id)
    elif User.is_admin(user):
        created_team = team_service.create_team(team_name, number_of_players, user.id)
    else:
        return JSONResponse(status_code=401, content='You must be an admin or a director to be able to create a team.')

    return created_team


@teams_router.get('/', description= 'Show all teams:')
def find_all_teams(x_token: str = Header(default=None)):
    
    if x_token is None:
        return JSONResponse(status_code=401, content='You must be logged in to view the list of teams.')
    
    user = get_user_or_raise_401(x_token)

    if User.is_spectator(user):
        list_of_teams = team_service.get_all_teams()
    elif User.is_player(user):
        list_of_teams = team_service.get_all_teams()
    elif User.is_director(user):
        list_of_teams = team_service.get_all_teams()
    elif User.is_admin(user):
        list_of_teams = team_service.get_all_teams()
    else: 
        return JSONResponse(status_code=401, content='Unrecognized credentials.')

    return list_of_teams


@teams_router.get('/id', description='Find team:')
def find_team_by_id(id:int = Query(..., description='Enter id of the team:'), x_token: str = Header(default=None)):
    
    if x_token is None:
        return JSONResponse(status_code=401, content='You must be logged in to see the teams information.')
    
    user = get_user_or_raise_401(x_token)

    # if not shared_service.id_exists(id, 'teams'):
    #         return JSONResponse(status_code=404, content=f'Team with id: {id} does not exist.')
    if User.is_spectator(user):
        team = team_service.get_team_and_players_by_id(id)
    elif User.is_player(user):
        team = team_service.get_team_and_players_by_id(id)
    elif User.is_director(user):
        team = team_service.get_team_and_players_by_id(id) 
    elif User.is_admin(user):
        team = team_service.get_team_and_players_by_id(id)
    else: 
        return JSONResponse(status_code=401, content='Unrecognized credentials.')
    return team


@teams_router.delete('/', description="Delete a team:")
def delete_team(id: int = Query(..., description='Enter ID of the team you want to delete:'), 
                x_token: str = Header(default=None)
                ):
    ''' Used for deleting a team through team.id. Only admins and owners can delete it.

    Args:
        - team.id: int(URL link)
        - JWT token
    
    Returns:
        - Deleted team
    '''

    if x_token == None:
        return JSONResponse(status_code=401, content='You must be logged in and be an admin or a director and owner to be able to delete a team.')    
    
    user = get_user_or_raise_401(x_token)

    team = team_service.get_team_by_id(id)
    
    if User.is_admin(user):
        team_service.delete_team(id)
    elif User.is_director(user):
        if user.id == team.owners_id:
            team_service.delete_team(id)
        else:
            return JSONResponse(status_code=401, content='You must be the owner of the tеam to be able to delete it.')
    else:    
        return JSONResponse(status_code=401, content='You must be logged in and be an admin or a director and owner to be able to delete a team.')
        
    return {'Team is deleted.'}