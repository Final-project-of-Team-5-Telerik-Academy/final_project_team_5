from my_models.model_team import Team
from my_models.model_player import Player
from data.database import read_query, insert_query, update_query, read_query_additional
from services.shared_service import full_name_exists
from fastapi.responses import JSONResponse


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
