from data.database import insert_query, read_query, update_query
from my_models.model_match import Match
from my_models.model_player import Player
from fastapi.responses import JSONResponse
from services import date_service
import random
from datetime import date
from services import player_service



def get_all_matches(status: str, sort: str):
    sql = 'SELECT id, format, game_type, participant_1, participant_2, date, winner, tournament_name FROM matches '
    today = date_service.current_date()
    where_clause = []

    if status == 'upcoming':
        where_clause.append(f"WHERE date > '{today}'")

    if status == 'played':
        where_clause.append(f"WHERE date < '{today}'")

    where_clause.append(f'ORDER BY id {sort}')

    sql += ' '.join(where_clause)
    result = (Match.from_query_result(*row) for row in read_query(sql))

    if status == 'upcoming' and len(list(result)) == 0:
        return f'No upcoming matches for now.'
    return result



def get_match_by_id(id: int):
    row_data = read_query('''SELECT id, format, game_type, participant_1, participant_2, date, winner, tournament_name 
    FROM matches WHERE id = ?''', (id,))

    if len(row_data) == 0:
        return  None

    data = row_data[0]
    result = Match.from_query_result(*data)
    return result





def create_match(format: str, game_type: str, participant_1: str, participant_2: str, date):
    generated_match = insert_query('''INSERT INTO matches (format, game_type, participant_1, participant_2, date) 
                                    VALUES (?, ?, ?, ?, ?)''',
                                   (format, game_type, participant_1, participant_2, date))

    match_id = generated_match
    result = Match.from_query_result(id=match_id,
                   format = format,
                   game_type = game_type,
                   participant_1 = participant_1,
                   participant_2 = participant_2,
                   date = date,
                   winner='Тhe match has not been played yet',
                   tournament_name = 'add tournament name if needed')
    return result


# def match_winner():
#     score = {1:[1, 0], 2:[1, 0], 3:[1, 0], 4:[1, 0], 5:[1, 0],
#              6:[0, 1], 7:[0, 1], 8:[0, 1], 9:[0, 1], 10:[0, 1],
#              11:[1, 'ko'], 12:['ko', 1]}
#
#     numbers = range(1, 13)
#     chance = random.choice(numbers)
#     result = score[chance]
#
#     return result




def play_match(today: date):
    today = date_service.current_date()
    row_data = read_query(f"""SELECT id, format, game_type, participant_1, participant_2, date, winner, tournament_name 
    FROM matches WHERE isnull(winner) AND date < '{today}'""")

    upcoming_matches = (Match.from_query_result(*row) for row in row_data)

    for current_match in upcoming_matches:
        participant_1 = player_service.get_player_by_full_name(current_match.participant_1)
        participant_2 = player_service.get_player_by_full_name(current_match.participant_2)

        players = [1, 2]
        winner_id = random.choice(players)
        winner_name = participant_1.full_name if winner_id == 1 else participant_2.full_name

    # update match detail
        update_query('''UPDATE matches SET winner = ? WHERE id = ?''',
                     (winner_name, current_match.id))

        # participant 1 result
        update_statistics(participant_1.full_name,
                          participant_2.full_name,
                          win = 1 if winner_id == 1 else 0,
                          loss = 0 if winner_id == 1 else 1,
                          matches_id=current_match.id,
                          tournament_name = current_match.tournament_name,
                          date = current_match.date)

    # participant 2 result
        update_statistics(participant_2.full_name,
                          participant_1.full_name,
                          win = 0 if winner_id == 1 else 1,
                          loss = 1 if winner_id == 1 else 0,
                          matches_id = current_match.id,
                          tournament_name = current_match.tournament_name,
                          date = current_match.date)



def update_statistics(player_name: str, opponent_name: str, win: int,
                      loss: int, matches_id: int, tournament_name: int, date):
    insert_query('''INSERT INTO players_has_matches (player_name, opponent_name, win, loss, matches_id, tournament_name, date) 
                    VALUES (?, ?, ?, ?, ?, ?, ?)''',
                 (player_name, opponent_name, win, loss, matches_id, tournament_name, date))





