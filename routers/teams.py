from fastapi import APIRouter, Header, Query
from services import team_service


teams_router = APIRouter(prefix='/teams', tags={'Teams'})


@teams_router.post('/', description='Create a new team:')
def create_team(team_name: str = Query(..., description='Enter full name of team:'),
                  number_of_players: int = Query(..., description='Enter number of players:'),
                  x_token: str = Header()):
    ''' Used for creating a new team by a director or admin.

    Args:
        - team_name: str(Query)
        - number_of_players: int(Query)
        - x_token: JWT token(Header)

    Returns:
        - Created team information
    '''

    return team_service.create_a_team(team_name, number_of_players, x_token)


@teams_router.get('/', description= 'Show all teams:')
def find_all_teams(x_token: str = Header()):
    ''' Used to get all teams.
    
    Args:
        - JWT token(Header)
    
    Returns:
        - list of all teams
    '''

    return team_service.find_all_teams(x_token)


@teams_router.get('/id', description='Find team:')
def find_team_by_id(id:int = Query(..., description='Enter id of the team:'), x_token: str = Header()):
    ''' Used to to get a team by id.
    
    Args:
        - JWT token(Header)
    
    Returns:
        - team
    '''

    return team_service.find_team_by_id(id, x_token)


@teams_router.delete('/', description="Delete a team:")
def delete_team(id: int = Query(..., description='Enter ID of the team you want to delete:'), 
                x_token: str = Header()
                ):
    ''' Used for deleting a team through team.id. Only admins and owners can delete it.

    Args:
        - team.id: int(URL link)
        - JWT token
    
    Returns:
        - Deleted team
    '''

    return team_service.delete_team_by_id(id, x_token)


@teams_router.post('/players/{id}', description="Add player to a team:")
def add_player_to_team(players_id: int = Query(..., description='Enter ID of the player you want to add:'), teams_id: int = Query(..., description='Enter ID of the team:'), 
                x_token: str = Header()
                ):
    ''' Used for adding a player to a team.

    Args:
        - players_id: int(URL link)
        - teams_id: int(URL link)
        - JWT token
    
    Returns:
        - Added player
    '''

    return team_service.add_player_to_a_team(players_id, teams_id, x_token)


@teams_router.delete('/players/{id}', description="Remove player from a team:")
def remove_player_from_team(players_id: int = Query(..., description='Enter ID of the player you want to remove:'), teams_id: int = Query(..., description='Enter ID of the team:'), 
                x_token: str = Header()
                ):
    ''' Used for deleting a player from a team.

    Args:
        - players_id: int(URL link)
        - teams_id: int(URL link)
        - JWT token
    
    Returns:
        - Removed player
    '''

    return team_service.delete_player_from_team(players_id, teams_id, x_token)