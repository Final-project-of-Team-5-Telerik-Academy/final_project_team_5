from data.database import insert_query, read_query, update_query
from my_models.model_match import Match
from my_models.model_player import Player
from my_models.model_team import Team
from fastapi.responses import JSONResponse
import random
from datetime import date



" 1. GET ALL MATCHES"
def get_all_matches(status: str, sort: str):
    sql = '''SELECT id, match_format, game_type, sport, participant_1, participant_2, 
            creator, date, winner, tournament_name, stage FROM matches '''
    where_clause = []

    if status == 'played':
        where_clause.append(f"WHERE winner <> 'not played'")

    elif status == 'upcoming':
        where_clause.append(f"WHERE winner = 'not played'")

    where_clause.append(f'ORDER BY date {sort}')
    sql += ' '.join(where_clause)
    row_data = read_query(sql)

    if len(list(row_data)) == 0:
        return f'No matches for now.'

    result = []
    for el in row_data:
        match_dict = Match.from_query_result(*el)
        result.append(match_dict)

    return result



" 1.1 GET ALL MATCHES BY TOURNAMENT"
def get_matches_by_tournament(title: str):
    row_data = read_query(f'''SELECT id, match_format, game_type, sport, participant_1, participant_2, 
            creator, date, winner, tournament_name, stage FROM matches 
            WHERE tournament_name = ?''', (title, ))

    result = []
    for el in row_data:
        match_dict = Match.from_query_result(*el)
        result.append(match_dict)
    return result




" 2. GET MATCH BY ID"
def get_match_by_id(match_id: int):
    row_data = read_query('''SELECT id, match_format, game_type, sport, participant_1, 
        participant_2, creator, date, winner, tournament_name, stage 
        FROM matches WHERE id = ?''', (match_id,))

    if len(row_data) == 0:
        return  None

    data = row_data[0]
    result = Match.from_query_result(*data)
    return result




" 3. CREATE A MATCH"
def create_match(match_format: str, game_type: str, sport: str, participant_1: str,
                 participant_2: str, creator_name: str, m_date: date, t_title: str, stage: int = 0):
    winner = 'not played'
    generated_match = insert_query('''INSERT INTO matches (match_format, game_type, sport, participant_1, 
                                    participant_2, creator, date, winner, tournament_name, stage) 
                                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                                   (match_format, game_type, sport, participant_1, participant_2,
                                    creator_name, m_date, winner, t_title, stage))

    match_id = generated_match
    result = Match.from_query_result(id = match_id,
                                     match_format = match_format,
                                     game_type = game_type,
                                     sport = sport,
                                     participant_1 = participant_1,
                                     participant_2 = participant_2,
                                     creator = creator_name,
                                     date = m_date,
                                     winner = winner,
                                     tournament_name = t_title,
                                     stage = stage)
    return result



" 4. ENTER WINNER"
def enter_match_winner(match: Match, p1_score, p2_score):
# ONE ON ONE
    if match.game_type == 'one on one':
        p_type = 'player'
        participant_1 = get_player_by_full_name_v2(match.participant_1)
        p1_name = participant_1.full_name
        participant_2 = get_player_by_full_name_v2(match.participant_2)
        p2_name = participant_2.full_name

# TEAM GAME
    else:
        p_type = 'team'
        participant_1 = get_team_by_name_v2(match.participant_1)
        p1_name = participant_1.team_name
        participant_2 = get_team_by_name_v2(match.participant_2)
        p2_name = participant_2.team_name

# check tournament stage - the new tournament stage is set after matches creation
    t_title = match.tournament_name
    if t_title != 'not part of a tournament':
        stage_data = read_query('SELECT stage FROM tournaments WHERE title = ?',
                                (t_title,))
        current_stage = stage_data[0][0]
    else:
        current_stage = 0

# TIME vs SCORE LIMIT
    if match.match_format == 'score limit':
        p1_score, p2_score = int(p1_score), int(p2_score)
        p1_win, p1_loss, p2_win, p2_loss, winner, p1_stage, p2_stage = score_winner(
            p1_score, p2_score, p1_name, p2_name, current_stage)

    else:   # time limit
        p1_score, p2_score = float(p1_score), float(p2_score)
        p1_win, p1_loss, p2_win, p2_loss, winner, p1_stage, p2_stage = time_winner(
            p1_score, p2_score, p1_name, p2_name, current_stage)

# update matches
    update_query('''UPDATE matches SET winner = ? WHERE id = ?''',
                 (winner, match.id))

# update participant 1
    update_statistics(p_type,
                      participant_1.id, p1_name, p1_score,
                      p2_name, p2_score,
                      win = p1_win,
                      loss = p1_loss,
                      matches_id = match.id,
                      tournament_name = match.tournament_name,
                      tournament_trophy = 0,
                      m_date= match.date,
                      stage = p1_stage)

    update_tournaments_participants_stage(t_title, p_type, p1_stage, participant_1.id)


# update participant 2
    update_statistics(p_type,
                      participant_2.id, p2_name, p2_score,
                      p1_name, p1_score,
                      win = p2_win,
                      loss = p2_loss,
                      matches_id = match.id,
                      tournament_name = match.tournament_name,
                      tournament_trophy = 0,
                      m_date= match.date,
                      stage = p2_stage)

    update_tournaments_participants_stage(t_title, p_type, p2_stage, participant_2.id)

    if winner == 'draw':
        return {'message': f'Match id: {match.id} ended in a draw.'}
    elif winner == 'draw' and current_stage > 0:
        return {'message': f'Match id: {match.id}, part of {t_title}, ended in a draw.'}
    elif current_stage == 0:
        return {'message': f'The winner of match  id: {match.id}, part of {t_title}, is {winner}. Results {p1_name} vs {p2_name} - {p1_score} : {p2_score}!'}
    return {'message': f'The winner of match id: {match.id} is {winner}. Results {p1_name} vs {p2_name} - {p1_score} : {p2_score}!'}





" 4.1 SCORE WINNER"
def score_winner(p1_score: int, p2_score, p1_name: str, p2_name:str, current_stage: int):
# participant 1 winner
    p1_stage, p2_stage = 0, 0
    if p1_score > p2_score:
        winner = p1_name
        p1_win, p1_loss = 1, 0
        p2_win, p2_loss = 0, 1
        if current_stage > 0:
            p1_stage = current_stage + 1
            p2_stage = current_stage

# participant 2 winner
    elif p1_score < p2_score:
        winner = p2_name
        p1_win, p1_loss = 0, 1
        p2_win, p2_loss = 1, 0
        if current_stage > 0:
            p1_stage = current_stage
            p2_stage = current_stage + 1

# draw
    else:
        winner = 'draw'
        p1_win, p1_loss = 0, 0
        p2_win, p2_loss = 0, 0
        p1_stage, p2_stage = current_stage + 1, current_stage  # on draw p1 gets walkover (служебна победа)

    return p1_win, p1_loss, p2_win, p2_loss, winner, p1_stage, p2_stage




" 4.2 TIME WINNER"
def time_winner(p1_score, p2_score, p1_name: str, p2_name:str, current_stage: int):
# participant 1 winner
    p1_stage, p2_stage = 0, 0
    if p1_score < p2_score:
        winner = p1_name
        p1_win, p1_loss = 1, 0
        p2_win, p2_loss = 0, 1
        if current_stage > 0:
            p1_stage = current_stage + 1
            p2_stage = current_stage

# participant 2 winner
    elif p1_score > p2_score:
        winner = p2_name
        p1_win, p1_loss = 0, 1
        p2_win, p2_loss = 1, 0
        if current_stage > 0:
            p1_stage = current_stage
            p2_stage = current_stage + 1

# draw
    else:
        winner = 'draw'
        p1_win, p1_loss = 0, 0
        p2_win, p2_loss = 0, 0
        p1_stage, p2_stage = current_stage + 1, current_stage  # on draw p1 gets walkover (служебна победа)

    return p1_win, p1_loss, p2_win, p2_loss, winner, p1_stage, p2_stage






" 4.3. UPDATE PARTICIPANT STATISTICS"
def update_statistics(p_type:str, participant_id: int, participant_name: str, participant_score: float,
                      opponent_name: str, opponent_score:float, win: int, loss: int, matches_id: int,
                      tournament_name: str, stage: int, m_date, tournament_trophy: int = 0):
    insert_query(f'''INSERT INTO {p_type}s_statistics ({p_type}s_id, {p_type}_name, {p_type}_score,
                opponent_name, opponent_score, win, loss, matches_id, tournament_name, tournament_trophy, stage, date) 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                 (participant_id, participant_name, participant_score, opponent_name,
                  opponent_score, win, loss, matches_id, tournament_name, tournament_trophy, stage, m_date))




" 4.4. UPDATE TOURNAMENTS_PARTICIPANTS STAGE"
def update_tournaments_participants_stage(title: str, p_type: str, new_stage: int, participant_id: int):
    update_query(f'''UPDATE tournaments_{p_type}s SET stage = ? 
                WHERE tournaments_title = ? AND {p_type}s_id = ?''',
                 (new_stage, title, participant_id))




" 4.5. CHECK TOURNAMENTS MATCHES ARE FINISHED"
def tournament_matches_are_finished(t_title: str):
    all_tournament_matches = get_matches_by_tournament(t_title)
    for match in all_tournament_matches:
        if match.winner == 'not played':
            return False
        return True




" 5. DELETE MATCH"
def delete_match(match_id: int):

    update_query(f'DELETE FROM teams_statistics WHERE matches_id = {match_id}')
    update_query(f'DELETE FROM players_statistics WHERE matches_id = {match_id}')
    update_query(f'DELETE FROM matches WHERE id = {match_id}')
    return {'message': f'Match with id {match_id} has been deleted.'}




" 6. MATCHES SIMULATIONS"
def matches_simulations():
    all_matches = get_all_matches('upcoming', 'asc')
    if all_matches == 'No matches for now.':
        return None

    output = []
    for current_match in all_matches:
        if current_match.match_format == 'score limit':
            p1_score = random.randint(0, 10)
            p2_score = random.randint(0, 10)
        else:   # time limit
            p1_score = round(random.uniform(2.01, 20.01), 2)
            p2_score = round(random.uniform(2.01, 20.01), 2)

        result = enter_match_winner(current_match, p1_score, p2_score)
        output.append(result)

    return output




def get_player_by_full_name_v2(full_name: str):
    row_data = read_query('''SELECT id, full_name, country, sports_club, is_active, is_connected, 
                        teams_id, blocked_players_id FROM players WHERE full_name = ?''',
                          (full_name,))

    if not row_data:
        return None

    data = row_data[0]
    result = Player.from_query_result(*data)
    return result




def get_team_by_name_v2(name: str):
    row_data = read_query('''SELECT id, team_name, number_of_players, owners_id 
                                FROM teams where team_name = ?''', (name,))
    if not row_data:
        return None
    data = row_data[0]
    actual = Team.from_query_result(*data)
    return actual




def get_knockout_matches_by_tournament(title: str, stage: int):
    row_data = read_query('''SELECT id, match_format, game_type, sport, participant_1, participant_2, 
            creator, date, winner, tournament_name, stage FROM matches 
            WHERE tournament_name = ? AND stage = ?''', (title, stage, ))

    if row_data is None:
        return JSONResponse(status_code=404, content=f'There are no matches for tournament "{title}"')
    else:
        result = []
        for el in row_data:
            match_dict = Match.from_query_result(*el)
            result.append(match_dict)
        return result



