from my_models.model_team import Team
from my_models.model_player import Player
from data.database import read_query, insert_query, update_query, read_query_additional
from services.shared_service import full_name_exists
from fastapi.responses import JSONResponse
from authentication.authenticator import get_user_or_raise_401
from my_models.model_user import User


def team_name_exists(team_name: str) -> bool:
    ''' Used to check if the team_name exists in teams in the database.'''

    return any(
        read_query(
            f'SELECT team_name FROM teams WHERE team_name = ?',
            (team_name,)))


def team_id_exists(id: int) -> bool:
    ''' Used to check if the id exists in teams in the database.'''

    return any(
        read_query(
            f'SELECT id FROM teams WHERE id = ?',
            (id,)))


def create_team(team_name: str, number_of_players: int, owners_id: int) -> Team:
    ''' Used for creating a new team and saving it in the database.

    Args:
        - team_name: str
        - number_of_players: str
        - owners_id: int

    Returns:
        - Created team information
    '''

    if team_name_exists(team_name):
        return JSONResponse(status_code=400, content=f'The full name: {team_name} is already taken!')
    
    generated_id = insert_query(
        'INSERT INTO teams(team_name, number_of_players, owners_id) VALUES (?,?,?)',
        (team_name, number_of_players, owners_id)  
    )

    return Team(
        id=generated_id,
        team_name=team_name,
        number_of_players=number_of_players,
        owners_id=owners_id
    )


def get_all_teams() -> Team | None:
    ''' Search in the database and creates a list of all teams. 
    
    Returns:
        - a list of all teams(id, team_name, number_of_players, owners_id)
    '''

    data = read_query('SELECT id, team_name, number_of_players, owners_id FROM teams')

    result = (Team.from_query_result(*row) for row in data)

    return result


def get_team_by_id(id: int) -> Team | None:
    ''' Used for getting a single team by team.id.
    
    Args:
        - team.id: int(URL link)
    
    Returns:
        - team
    '''

    team = read_query_additional('SELECT id, team_name, number_of_players, owners_id FROM teams where id = ?',(id,))

    if team is None:
        return JSONResponse(status_code=404, content=f'Team with id: {id} does not exist.')

    actual = Team.from_query_result(*team)

    return actual


def get_team_and_players_by_id(id: int) -> Team | None:
    ''' Used for getting a single team by team.id.
    
    Args:
        - team.id: int(URL link)
    
    Returns:
        - team
    '''

    team = read_query_additional('SELECT id, team_name, number_of_players, owners_id FROM teams where id = ?',(id,))

    if team is None:
        return JSONResponse(status_code=404, content=f'Team with id: {id} does not exist.')

    actual = Team.from_query_result(*team)

    team_players = read_query('''SELECT * FROM players where teams_id = ?''', (id,))

    players = [Player.from_query_result(*player) for player in team_players]
    actual.players = players

    return actual


def delete_team(id: int):
    ''' Used for deleting the team from the database.'''

    teams_id = None
    update_query('''UPDATE players SET teams_id = ? WHERE teams_id = ?''',
                (teams_id, id))

    insert_query('''DELETE FROM teams WHERE id = ?''',
                 (id,))


def create_a_team(team_name: str, number_of_players: int, x_token: str):
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
        created_team = create_team(team_name, number_of_players, user.id)
    elif User.is_admin(user):
        created_team = create_team(team_name, number_of_players, user.id)
    else:
        return JSONResponse(status_code=401, content='You must be an admin or a director to be able to create a team.')

    return created_team


def get_all_teams(x_token: str):
    ''' Used to get all teams.
    
    Args:
        - JWT token(Header)
    
    Returns:
        - list of all teams
    '''

    if x_token is None:
        return JSONResponse(status_code=401, content='You must be logged in to view the list of teams.')
    
    user = get_user_or_raise_401(x_token)

    if User.is_spectator(user):
        list_of_teams = get_all_teams()
    elif User.is_player(user):
        list_of_teams = get_all_teams()
    elif User.is_director(user):
        list_of_teams = get_all_teams()
    elif User.is_admin(user):
        list_of_teams = get_all_teams()
    else: 
        return JSONResponse(status_code=401, content='Unrecognized credentials.')

    return list_of_teams


def get_team_by_id(id: int, x_token: str):
    ''' Used to to get a team by id.
    
    Args:
        - JWT token(Header)
    
    Returns:
        - team
    '''

    if x_token is None:
        return JSONResponse(status_code=401, content='You must be logged in to see the teams information.')
    
    user = get_user_or_raise_401(x_token)

    if User.is_spectator(user):
        team = get_team_and_players_by_id(id)
    elif User.is_player(user):
        team = get_team_and_players_by_id(id)
    elif User.is_director(user):
        team = get_team_and_players_by_id(id) 
    elif User.is_admin(user):
        team = get_team_and_players_by_id(id)
    else: 
        return JSONResponse(status_code=401, content='Unrecognized credentials.')
    return team


def delete_team_by_id(id: int, x_token: str):
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

    team = get_team_and_players_by_id(id)
    
    if User.is_admin(user):
        delete_team(id)
    elif User.is_director(user):
        if user.id == team.owners_id:
            delete_team(id)
        else:
            return JSONResponse(status_code=401, content='You must be the owner of the team to be able to delete it.')
    else:    
        return JSONResponse(status_code=401, content='You must be logged in and be an admin or a director and owner to be able to delete a team.')
        
    return {'Team is deleted.'}