from my_models.model_team import Team
from my_models.model_player import Player
from data.database import read_query, insert_query, update_query, read_query_additional
from fastapi.responses import JSONResponse
from authentication.authenticator import get_user_or_raise_401
from my_models.model_user import User
from services import shared_service


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
        - number_of_players: int
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

    # result = (Team.from_query_result(*row) for row in data)
    result = (Team.from_query_result(*row) for row in data),

    return result


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


def teams_list_exists() -> bool:
    ''' Used to check if there is any registered team in the database.'''

    return any(
        read_query(
            'SELECT id, team_name, number_of_players, owners_id FROM teams',
            ))


def remove_player_from_the_team(players_id: int, teams_id: int):
    ''' Used for deleting player from the team from the database.'''
    team = None

    update_query('''UPDATE players SET teams_id = ? WHERE id = ? and teams_id = ?''',
                (team, players_id, teams_id))


def add_player_to_team(players_id: int, teams_id: int):
    ''' Used for deleting player from the team from the database.'''

    update_query('''UPDATE players SET teams_id = ? WHERE id = ?''',
                (teams_id, players_id))
    

def player_with_team_id_exists(players_id: int, teams_id: int) -> bool:
    ''' Used to check if the teams_id exists in the specific player in the database.

    Returns:
        - True/False
    '''

    return any(
        read_query('SELECT id FROM players WHERE id = ? and teams_id = ?',
            (players_id, teams_id)))


def create_a_team(team_name: str, number_of_players: int, x_token: str):
    ''' Used for creating a new team by a director or admin.

    Args:
        - team_name: str(Query)
        - number_of_players: int(Query)
        - x_token: JWT token(Header)

    Returns:
        - Created team information
    ''' 
    
    user = get_user_or_raise_401(x_token)

    if User.is_director(user):
        created_team = create_team(team_name, number_of_players, user.id)
    elif User.is_admin(user):
        created_team = create_team(team_name, number_of_players, user.id)
    else:
        return JSONResponse(status_code=401, content='You must be an admin or a director to be able to create a team.')

    return created_team


def find_all_teams(x_token: str):
    ''' Used to get all teams.
    
    Args:
        - JWT token(Header)
    
    Returns:
        - list of all teams
    '''

    if x_token is None:
        return JSONResponse(status_code=401, content='You must be logged in to view the list of teams.')
    elif not teams_list_exists():
        return JSONResponse(status_code=404, content='There are no teams.')
    
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


def find_team_by_id(id: int, x_token: str):
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
    
    user = get_user_or_raise_401(x_token)

    team = get_team_and_players_by_id(id)

    if not shared_service.id_exists(id, 'teams'):
        return JSONResponse(status_code=404, content=f'Team with id: {id} does not exist.')
    elif User.is_admin(user):
        delete_team(id)
    elif User.is_director(user):
        if user.id == team.owners_id:
            delete_team(id)
        else:
            return JSONResponse(status_code=401, content='You must be the owner of the team to be able to delete it.')
    else:    
        return JSONResponse(status_code=401, content='You must be logged in and be an admin or a director and owner to be able to delete a team.')
        
    return {'Team is deleted.'}


def get_team_by_name(name: str) -> Team | None:
    ''' Used for getting a single team by team.name.

    Args:
        - team.id: int(URL link)

    Returns:
        - team
    '''

    team = read_query_additional('SELECT id, team_name, number_of_players, owners_id FROM teams where team_name = ?', (name,))

    if team is None:
        return JSONResponse(status_code=404, content=f'Team with name: {name} does not exist.')

    actual = Team.from_query_result_additional(*team)

    return actual


def delete_player_from_team(players_id: int, teams_id, x_token: str):
    ''' Used for deleting a player from a team. Only admins and owners can delete it.

    Args:
        - players_id: int(URL link)
        - teams_id: int(URL link)
        - JWT token
    
    Returns:
        - Deleted player from team
    '''
    
    user = get_user_or_raise_401(x_token)

    team = get_team_and_players_by_id(teams_id)

    if not player_with_team_id_exists(players_id, teams_id):
        return JSONResponse(status_code=404, content=f'Player with id: {players_id} is currently not in the team.')
    elif User.is_admin(user):
        remove_player_from_the_team(players_id, teams_id)
    elif User.is_director(user):
        if user.id == team.owners_id:
            remove_player_from_the_team(players_id, teams_id)
    else:    
        return JSONResponse(status_code=401, content='You must be logged in and be an admin or a director and owner to be able to remove a player.')
        
    return {'Player is removed from the team.'}


def add_player_to_a_team(players_id: int, teams_id, x_token: str):
    ''' Used for adding a player to a team.

    Args:
        - players_id: int(URL link)
        - teams_id: int(URL link)
        - JWT token
    
    Returns:
        - Added player
    '''
    
    user = get_user_or_raise_401(x_token)

    team = get_team_and_players_by_id(teams_id)

    if not shared_service.id_exists(players_id, 'players'):
        return JSONResponse(status_code=400, content=f'Player with id: {players_id} does not exist.')
    elif not shared_service.id_exists(teams_id, 'teams'):
        return JSONResponse(status_code=404, content=f'Team with id: {teams_id} does not exist.')
    elif player_with_team_id_exists(players_id, teams_id):
        return JSONResponse(status_code=404, content=f'Player with id: {players_id} is currently in a team.')
    elif User.is_admin(user):
        add_player_to_team(players_id, teams_id)
    elif User.is_director(user):
        if user.id == team.owners_id:
            add_player_to_team(players_id, teams_id)
    else:    
        return JSONResponse(status_code=401, content='You must be logged in and be an admin or a director and owner to be able to add a player.')
        
    return {'Player is added to the team.'}
