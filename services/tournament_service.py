from pydantic import constr
from data.database import insert_query, read_query, update_query
from my_models.model_tournament import Tournament
from datetime import date
from my_models.model_user import User
from my_models.model_player import Player
from my_models.model_tournament import Tournament


def create_tournament(title: str, format: str, date: date, prize: int, game_type: str, creator: User):

    generated_tournament = insert_query(
        '''INSERT INTO tournaments (title, format, date, prize, users_creator_id, game_type)
        VALUE (?, ?, ?, ?, ?, ?)''',(title, format, date, prize, creator.id, game_type))

    result = Tournament(id = generated_tournament,
                        title = title,
                        format = format,
                        date = date,
                        prize = prize,
                        game_type = game_type,
                        creator = creator.full_name,
                        is_finished = False,
                        players_or_teams = 'Add players/teams to the tournament')
    return result



def get_tournament_id_by_title(title: str):
    tournament_id = read_query('SELECT id FROM tournaments WHERE title = ?', (title,))
    return None if not tournament_id else tournament_id


def get_tournament_by_title(title: str):
    row_data = read_query(f'SELECT * FROM tournaments WHERE title = {title}')
    tournament = Tournament.from_query_result(*row_data)

    return None if not tournament else tournament



def get_game_format(t_title):
    game_format = read_query(f'SELECT team_game_or_one_on_one FROM tournaments WHERE title = {t_title}')
    return game_format


def add_player_or_team(player: Player, tournament: Tournament):
    tournament.players_or_teams.append(player)
    insert_query('''INSERT INTO tournaments () 
                    SET''')

    result = {
        'id': f'{tournament.id}',
        'title': f'{tournament.title}',
        'format': f'{tournament.format}',
        'date': f'{tournament.date}',
        'prize': f'{tournament.prize}',
        'game type': f'{tournament.game_type}',
        'creator': f'{tournament.creator}',
        'is finished': f'{tournament.is_finished}',
        'players or teams': f'{tournament.players_or_teams}'}

    return result

















