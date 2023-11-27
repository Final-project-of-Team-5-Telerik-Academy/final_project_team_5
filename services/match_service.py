from data.database import insert_query, read_query, update_query
from my_models.model_match import Match
from my_models.model_player import Player
from fastapi.responses import JSONResponse
from services import date_service
import random
from datetime import date
from services import player_service, tournament_service



def get_all_matches(status: str, sort: str):
    sql = 'SELECT id, match_format, game_type, participant_1, participant_2, date, winner, tournament_name, tournament_stage FROM matches '
    today = date_service.current_date()
    where_clause = []

    if status == 'played':
        where_clause.append(f"WHERE date < '{today}'")

    elif status == 'upcoming':
        where_clause.append(f"WHERE date > '{today}'")


    where_clause.append(f'ORDER BY date {sort}')
    sql += ' '.join(where_clause)
    row_data = read_query(sql)

    if status == 'upcoming' and len(list(row_data)) == 0:
        return f'No upcoming matches for now.'

    result = []
    for el in row_data:
        match_dict = {
            'id': el[0],
            'match format': el[1],
            'game type': el[2],
            'participant 1': el[3],
            'participant 2': el[4],
            'date': el[5],
            'winner': el[6],
            'tournament name': el[7],
            'tournament stage': el[8]}
        result.append(match_dict)

    return result



def get_match_by_id(id: int):
    row_data = read_query('''SELECT id, match_format, game_type, participant_1, participant_2, date, winner, tournament_name, tournament_stage 
    FROM matches WHERE id = ?''', (id,))

    if len(row_data) == 0:
        return  None

    data = row_data[0]
    result = Match.from_query_result(*data)
    return result





def create_match(match_format: str, game_type: str, participant_1: str, participant_2: str,
                 date: date, t_title: str, stage: int | None = None):
    winner = 'not played'
    generated_match = insert_query('''INSERT INTO matches (match_format, game_type, participant_1, 
                                    participant_2, date, winner, tournament_name, stage) 
                                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                                   (match_format, game_type, participant_1, participant_2,
                                    date, winner, t_title, stage))

    match_id = generated_match
    result = Match.from_query_result(id=match_id,
                                     match_format = match_format,
                                     game_type = game_type,
                                     participant_1 = participant_1,
                                     participant_2 = participant_2,
                                     date = date,
                                     winner = winner,
                                     tournament_name = t_title,
                                     stage = stage)
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




def play_match_one_on_one(new_date: date):
    tournament_service.tournaments_stage()
# check for unfinished matches
    matches_row_data = read_query("""SELECT id, match_format, game_type, participant_1, 
        participant_2, date, winner, tournament_name, stage 
        FROM matches WHERE winner = ? AND date <= ?""", ('not played', new_date))
    upcoming_matches = (Match.from_query_result(*row) for row in matches_row_data)

    for current_match in upcoming_matches:
        participant_1 = player_service.get_player_by_full_name(current_match.participant_1)
        participant_2 = player_service.get_player_by_full_name(current_match.participant_2)

        players = [1, 2]
        winner_id = random.choice(players)
        winner_name = participant_1.full_name if winner_id == 1 else participant_2.full_name

        update_query('''UPDATE matches SET winner = ? WHERE id = ?''',
                     (winner_name, current_match.id))

    # update players_statistics
        update_single_player_statistics(participant_1.id, participant_1.full_name,
                                        participant_2.full_name,
                                        win = 1 if winner_id == 1 else 0,
                                        loss = 0 if winner_id == 1 else 1,
                                        matches_id=current_match.id,
                                        tournament_name = current_match.tournament_name,
                                        date = current_match.date,
                                        stage = current_match.stage)

        update_single_player_statistics(participant_2.id, participant_2.full_name,
                                        participant_1.full_name,
                                        win = 0 if winner_id == 1 else 1,
                                        loss = 1 if winner_id == 1 else 0,
                                        matches_id = current_match.id,
                                        tournament_name = current_match.tournament_name,
                                        date = current_match.date,
                                        stage = current_match.stage)

    # update tournaments_players
        if current_match.tournament_name != 'not part of a tournament':
            t_title = current_match.tournament_name
            tournament_id = tournament_service.get_tournament_id_by_title(t_title)
            stage = int(current_match.stage) + 1
            insert_query('''INSERT INTO tournaments_players (players_id, player_name, 
                tournaments_id, tournament_title, stage) VALUES (?, ?, ?, ?, ?)''',
                (winner_id, winner_name, tournament_id, t_title, stage))

        # prize for winner
            last = last_players(t_title)
            if len(last) == 1:
                finish_tournament(winner_name, t_title)


# check for unfinished tournaments
    today = date_service.current_date()
    tournament_service.get_unfinished_tournaments()
    play_match_one_on_one(today)



def last_players(t_title: str):
    stage_data = read_query('''SELECT stage FROM tournaments_players 
        WHERE tournament_title = ? ORDER BY stage DESC LIMIT 1''', (t_title,))
    last_stage = stage_data[0][0]

    data = read_query('''SELECT player_name FROM tournaments_players 
        WHERE tournament_title = ? ORDER BY stage DESC LIMIT 1''',
        (t_title,))

    return data[0]



def finish_tournament(winner: str, t_title: str):
    update_query('''UPDATE tournaments SET winner = ? WHERE title = ?''',
                 (winner, t_title))
    update_query('UPDATE players_statistics SET tournament_trophy = 1 WHERE player_name = ?',
                 (winner, ))




def update_single_player_statistics(player_id: int, player_name: str, opponent_name: str, win: int,
                                    loss: int, matches_id: int, tournament_name: int, date, stage: int):
    insert_query('''INSERT INTO players_statistics (players_id, player_name, 
                    opponent_name, win, loss, matches_id, tournament_name, stage, date) 
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                 (player_id, player_name, opponent_name, win, loss,
                  matches_id, tournament_name, stage, date))


# def update_tournament_players(winner_player_name: str, t_title:str, stage):
#     insert_query()



def check_for_unfinished_matches(today: date):
    unfinished_matches = read_query('''SELECT id, match_format, game_type, participant_1, 
        participant_2, date, winner, tournament_name, stage 
        FROM matches WHERE is null (winner) AND date < ?''', (today,))

    if unfinished_matches:
        return True
    return False

