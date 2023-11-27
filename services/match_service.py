from data.database import insert_query, read_query, update_query
from my_models.model_match import Match
from my_models.model_player import Player
from fastapi.responses import JSONResponse
import random
from datetime import date
from services import player_service, team_service, tournament_service



" 1. GET ALL MATCHES"
def get_all_matches(status: str, sort: str):
    sql = 'SELECT id, match_format, game_type, participant_1, participant_2, date, winner, tournament_name, tournament_stage FROM matches '
    where_clause = []

    if status == 'played':
        where_clause.append(f"WHERE winner <> 'not played''")

    elif status == 'upcoming':
        where_clause.append(f"WHERE winner = 'not played'")


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



" 2. GET MATCH BY ID"
def get_match_by_id(id: int):
    row_data = read_query('''SELECT id, match_format, game_type, participant_1, participant_2, date, winner, tournament_name, tournament_stage 
    FROM matches WHERE id = ?''', (id,))

    if len(row_data) == 0:
        return  None

    data = row_data[0]
    result = Match.from_query_result(*data)
    return result



" 3. CREATE A MATCH"
def create_match(match_format: str, game_type: str, participant_1: str, participant_2: str,
                 creator_name, date: date, t_title: str, stage: int | None = None):
    winner = 'not played'
    generated_match = insert_query('''INSERT INTO matches (match_format, game_type, participant_1, 
                                    participant_2, creator, date, winner, tournament_name, stage) 
                                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                                   (match_format, game_type, participant_1, participant_2,
                                    creator_name, date, winner, t_title, stage))

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



" 3.1. CHECK or CREATE PLAYER"
def check_create_player(player_name: str):
    existing_player = player_service.get_player_by_full_name(player_name)

    if existing_player is None:
        player_service.create_player(player_name, 'add country', 'add sport club')
        return {"Warning": f'''Participant 1 dose not exist in the system. We've created profile for him, but it is uncompleted. You must finish it!'''}

    elif existing_player.blocked_player_id == 1:
        return JSONResponse(status_code=400, content=f'Player {player_name} is blocked.')

    else:
        return player_name












def play_match_one_on_one(new_date: date):
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
        update_statistics(participant_1.id, participant_1.full_name,
                          participant_2.full_name,
                          win = 1 if winner_id == 1 else 0,
                          loss = 0 if winner_id == 1 else 1,
                          matches_id=current_match.id,
                          tournament_name = current_match.tournament_name,
                          date = current_match.date,
                          stage = current_match.stage)

        update_statistics(participant_2.id, participant_2.full_name,
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
    tournament_service.get_unfinished_tournaments()




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







# def update_tournament_players(winner_player_name: str, t_title:str, stage):
#     insert_query()



def check_for_unfinished_matches(today: date):
    unfinished_matches = read_query('''SELECT id, match_format, game_type, participant_1, 
        participant_2, date, winner, tournament_name, stage 
        FROM matches WHERE is null (winner) AND date < ?''', (today,))

    if unfinished_matches:
        return True
    return False



"SET WINNER"
def set_winner(winner: str, match: Match):
    update_query('''UPDATE matches SET winner = ? WHERE id = ?''',
                     (winner, match))

    if match.match_format == 'one on one':
        p_type = 'player'
        participant_1 = player_service.get_player_by_full_name(match.participant_1)
        participant_2 = player_service.get_player_by_full_name(match.participant_2)
        winner_obj = player_service.get_player_by_full_name(winner)
        winner_id = winner_obj.id

    elif match.match_format == 'team game':
        p_type = 'team'
        participant_1 = team_service.get_team_by_name(match.participant_1)
        participant_2 = team_service.get_team_by_name(match.participant_2)
        winner_obj = team_service.get_team_by_name(winner)
        winner_id = winner_obj.id

    update_statistics(p_type, participant_1.id, participant_1.full_name,
                      participant_2.full_name,
                      win = 1 if winner_id == participant_1.id else 0,
                      loss = 0 if winner_id == participant_1.id else 1,
                      matches_id = match.id,
                      tournament_name = match.tournament_name,
                      date = match.date,
                      stag = match.stage)

    update_statistics(participant_2.id, participant_2.full_name,
                      participant_1.full_name,
                      win = 0 if winner_id == participant_2.id else 1,
                      loss = 1 if winner_id == participant_2.id else 0,
                      matches_id = match.id,
                      tournament_name = match.tournament_name,
                      date = match.date,
                      stage = match.stage)

    return {'message': f'The winner ot match with id {match.id} is set to {winner}.'}



def update_statistics(p_type:str, participant_id: int, participant_name: str, opponent_name: str, win: int,
                      loss: int, matches_id: int, tournament_name: int, date, stage: int):
    insert_query(f'''INSERT INTO {p_type}_statistics ({p_type}_id, {p_type}_name, 
                opponent_name, win, loss, matches_id, tournament_name, stage, date) 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                (participant_id, participant_name, opponent_name, win, loss,
                 matches_id, tournament_name, stage, date))









