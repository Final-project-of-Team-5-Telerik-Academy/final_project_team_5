from data.database import insert_query, read_query, update_query
from my_models.model_match import Match
from my_models.model_player import Player
from my_models.model_user import User
from datetime import date
from pydantic import constr, conint
from fastapi.responses import JSONResponse
import random

def get_all_matches(status: bool, before_date = None):
    if before_date:
        data = read_query(
            f'''SELECT id, title, player_1, player_2, date, format, prize, is_part_of_a_tournament, played, winner
                          FROM match_score_db.matches"
                          WHERE played = ? AND date < ?''', (status, before_date))
    else:
        data = read_query(
            f'''SELECT id, title, player_1, player_2, date, format, prize, is_part_of_a_tournament, played, winner
                  FROM match_score_db.matches"
                  WHERE played = ?''', (status,))

    result = (Match.from_query_result(*row) for row in data)
    return result


def get_match_by_title(title: str):
    data = read_query(
        f'''SELECT id, title, player_1, player_2, date, format, prize, is_part_of_a_tournament, played, winner
         FROM match_score_db.matches 
         WHERE title LIKE "%{title}%"''')

    result = Match.from_query_result(*data)
    if result:
        return result
    return None


def get_sorted_matches(sort: str, status: bool):
    if sort == 'ascending':
        sort = 'ASC'
    else:
        sort = "DESC"

    data = read_query(f'''SELECT id, title, player_1, player_2, date, format, prize, is_part_of_a_tournament, played, winner
        FROM match_score_db.matches ORDERED BY title {sort}
        WHERE played = ?''', (status,))
    result = (Match.from_query_result(*row) for row in data)
    return result



def create_match(date, title: str, match_format: str, prize: int, creator: str):
    player_1 = 'Not assigned yet'
    player_2 = 'Not assigned yet'
    played = False
    winner = None

    generated_match = insert_query(
        '''INSERT INTO matches (title, player_1, player_2, date, format, prize, creator, played, winner)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
        (title, player_1, player_2, date, match_format, prize, creator, played, winner))

    result = Match(id=generated_match,
                   title=title,
                   date = date,
                   player_1 = 'You must add a player name',
                   player_2 = 'You must add a player name',
                   match_format = match_format,
                   prize = prize,
                   tournament_name = 'add tournament name if needed',
                   creator = creator,
                   played = False,
                   winner = 'Тhe match has not been played yet')
    return result



def match_winner():
    score = {1:[1, 0], 2:[1, 0], 3:[1, 0], 4:[1, 0], 5:[1, 0],
             6:[0, 1], 7:[0, 1], 8:[0, 1], 9:[0, 1], 10:[0, 1],
             11:[1, 'ko'], 12:['ko', 1]}

    numbers = range(1, 13)
    chance = random.choice(numbers)
    result = score[chance]

    return result



def update_match_results(player_1, player_2, date, winner):
    update_query(f'''UPDATE matches SET winner = ? 
        WHERE player_1 = ? AND player_2 = ? AND date = ?''', (winner, player_1, player_2, date))



def play_matches(before_date):
    upcoming_matches = get_all_matches(status=False, before_date=before_date)
    for current_match in upcoming_matches:
        result_p1, result_p2 = match_winner()

        player_1 = current_match.player_1
        player_2 = current_match.player_2

        # TODO: add match result to player

        winner = player_1 if result_p1 == 1 else player_2
        date = current_match.date
        update_match_results(player_1, player_2, date, winner)



def get_creator_full_name(table: str, title: str):
    creator_name = read_query(f'SELECT creator FROM {table} WHERE title = ?', (title, ))
    return creator_name if creator_name else None


def assign_player_to_match(match: Match, player: Player, team: int):
# insert into matches
    update_query(f'UPDATE matches SET player_{team} = ? WHERE id = ?',
                     (player.full_name, match.id))
# insert into matches_players
    insert_query('INSERT INTO matches_players (matches_id, team, players_id) VALUES (?, ?, ?)',
                 (match.id, team, player.id))



def change_player_team_in_match(match_title, player_name, desired_team):
    insert_query(f'UPDATE matches SET player_{desired_team} = ? WHERE title = ?',
                 (player_name, match_title))


def get_match_id_by_title(title: str):
    match_id = read_query('SELECT id FROM matches WHERE title = ?', (title,))
    if not match_id:
        return JSONResponse(status_code=404, content=f'Match "{title}" not found.')
    return match_id

def update_match_details(title: str, column: str, new_param):
    match_id = get_match_id_by_title(title)

    update_query('UPDATE matches SET ? = ? WHERE id = ?',
                 (column, new_param, match_id))







