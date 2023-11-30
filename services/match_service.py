from data.database import insert_query, read_query, update_query
from my_models.model_match import Match
from my_models.model_player import Player
from my_models.model_tournament import Tournament
from fastapi.responses import JSONResponse
import random
from datetime import date
from services import player_service, team_service, tournament_service



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


    if row_data is None:
        return JSONResponse(status_code=404, content=f'There are no matches for tournament "{title}"')
    else:
        result = []
        for el in row_data:
            match_dict = Match.from_query_result(*el)
            result.append(match_dict)
        return result



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



" 2. GET MATCH BY ID"
def get_match_by_id(id: int):
    row_data = read_query('''SELECT id, match_format, game_type, sport, participant_1, 
        participant_2, creator, date, winner, tournament_name, stage 
        FROM matches WHERE id = ?''', (id,))

    if len(row_data) == 0:
        return  None

    data = row_data[0]
    result = Match.from_query_result(*data)
    return result



" 3. CREATE A MATCH"
def create_match(match_format: str, game_type: str, sport: str, participant_1: str,
                 participant_2: str, creator_name: str, date: date, t_title: str, stage: int=0):
    winner = 'not played'
    generated_match = insert_query('''INSERT INTO matches (match_format, game_type, sport, participant_1, 
                                    participant_2, creator, date, winner, tournament_name, stage) 
                                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                                   (match_format, game_type, sport, participant_1, participant_2,
                                    creator_name, date, winner, t_title, stage))

    match_id = generated_match
    result = Match.from_query_result(id = match_id,
                                     match_format = match_format,
                                     game_type = game_type,
                                     sport = sport,
                                     participant_1 = participant_1,
                                     participant_2 = participant_2,
                                     creator = creator_name,
                                     date = date,
                                     winner = winner,
                                     tournament_name = t_title,
                                     stage = stage)
    return result



" 3.1. CHECK or CREATE PLAYER"
def check_create_player(player_name: str):
    existing_player = player_service.get_player_by_full_name(player_name)

    if existing_player is None:
        country, sports_club = 'add country', 'add sport club'
        is_active, is_connected = 0, 0
        teams_id, blocked_players_id = None, None

        generated_id = insert_query('''INSERT INTO players(full_name, country, 
            sports_club, is_active, is_connected, teams_id, blocked_players_id) 
            VALUES (?,?,?,?,?,?,?)''', (player_name, country, sports_club,
                                        is_active, is_connected, teams_id, blocked_players_id))

        new_player = Player.from_query_result(generated_id, player_name, country,
                sports_club, is_active, is_connected, teams_id, blocked_players_id)
        return new_player

    elif existing_player.blocked_players_id == 1:
        return JSONResponse(status_code=400, content=f'Player {player_name} is blocked.')






" 4. SET WINNER"
def enter_match_winner(match: Match, participant_1: Player, p1_score: float,
                       participant_2: Player, p2_score: float, tournament_trophy: int = 0):
    if p1_score > p2_score:
        winner = participant_1.full_name
    elif p2_score > p1_score:
        winner = participant_2.full_name
    else:
        winner = 'draw'
    update_query('''UPDATE matches SET winner = ? WHERE id = ?''',
                     (winner, match.id))

    p_type, winner_id = None, None
    if match.game_type == 'one on one':
        p_type = 'player'
        participant_1_name = participant_1.full_name
        participant_2_name = participant_2.full_name
        winner_obj = player_service.get_player_by_full_name(winner)
        winner_id = winner_obj.id

    elif match.game_type == 'team game':
        p_type = 'team'
        participant_1 = team_service.get_team_by_name(match.participant_1)
        participant_1_name = participant_1.team_name

        participant_2 = team_service.get_team_by_name(match.participant_2)
        participant_2_name = participant_2.team_name

        winner_obj = team_service.get_team_by_name(winner)
        winner_id = winner_obj.id

    update_statistics(p_type,
                      participant_1.id, participant_1_name, p1_score,
                      participant_2_name, p2_score,
                      win = 1 if winner_id == participant_1.id else 0,
                      loss = 0 if winner_id == participant_1.id else 1,
                      matches_id = match.id,
                      tournament_name = match.tournament_name,
                      tournament_trophy = tournament_trophy,
                      date = match.date,
                      stage = match.stage)

    update_statistics(p_type,
                      participant_2.id, participant_2_name, p2_score,
                      participant_1_name, p2_score,
                      win = 1 if winner_id == participant_2.id else 0,
                      loss = 0 if winner_id == participant_2.id else 1,
                      matches_id = match.id,
                      tournament_name = match.tournament_name,
                      tournament_trophy = tournament_trophy,
                      date = match.date,
                      stage = match.stage)

    return {'message': f'The winner ot match with id {match.id} is set to {winner}.'}




" 4.1. UPDATE STATISTICS"
def update_statistics(p_type:str, participant_id: int, participant_name: str, participant_score: float,
                      opponent_name: str, opponent_score:float, win: int, loss: int, matches_id: int,
                      tournament_name: str, stage: int, date, tournament_trophy: int = 0):
    insert_query(f'''INSERT INTO {p_type}s_statistics ({p_type}s_id, {p_type}_name, {p_type}_score,
                opponent_name, opponent_score, win, loss, matches_id, tournament_name, tournament_trophy, stage, date) 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                (participant_id, participant_name, participant_score, opponent_name,
                 opponent_score, win, loss, matches_id, tournament_name, tournament_trophy, stage, date))




" 5. DELETE MATCH"
def delete_match(id: int):

    update_query(f'DELETE FROM teams_statistics WHERE matches_id = {id}')
    update_query(f'DELETE FROM players_statistics WHERE matches_id = {id}')
    update_query(f'DELETE FROM matches WHERE id = {id}')
    return {'message': f'Match with id {id} has been deleted.'}




" 6. MATCHES SIMULATIONS"
def matches_simulations():
    all_matches = get_all_matches('upcoming', 'asc')

    output = []
    output.append('-= MATCHES SIMULATIONS RESULTS =-')
    for current_match in all_matches:
        if current_match.tournament_name != "not part of a tournament":
            continue
        participant_type = current_match.game_type
        if participant_type == 'one on one':
            p_type = 'player'
            participant_1 = player_service.get_player_by_full_name(current_match.participant_1)
            participant_1_name = participant_1.full_name
            participant_2 = player_service.get_player_by_full_name(current_match.participant_2)
            participant_2_name = participant_2.full_name
        else:
            p_type = 'team'
            participant_1 = team_service.get_team_by_name(current_match.participant_1)
            participant_1_name = participant_1.team_name
            participant_2 = team_service.get_team_by_name(current_match.participant_2)
            participant_2_name = participant_2.team_name

        if current_match.match_format == 'score limit':
            p1_score = random.randint(0, 10)
            p2_score = random.randint(0, 10)
        else:
            p1_score = random.uniform(2.01, 20.01)
            p2_score = random.uniform(2.01, 20.01)

        if p1_score > p2_score:
            winner_name = participant_1_name
            p1_win = 1
            p2_win = 0
        elif p1_score < p2_score:
            winner_name = participant_2_name
            p1_win = 0
            p2_win = 1
        else:
            winner_name = 'draw'
            p1_win = 0
            p2_win = 0

        update_query('''UPDATE matches SET winner = ? WHERE id = ?''',
                     (winner_name, current_match.id))

        update_statistics(p_type = p_type,
                          participant_id = participant_1.id,
                          participant_name = participant_1_name,
                          participant_score = p1_score,
                          opponent_name = participant_2_name,
                          opponent_score = p2_score,
                          win = p1_win,
                          loss = p2_win,
                          matches_id=current_match.id,
                          tournament_name = current_match.tournament_name,
                          tournament_trophy = 0,
                          stage = current_match.stage,
                          date = current_match.date)

        update_statistics(p_type = p_type,
                          participant_id = participant_2.id,
                          participant_name = participant_2_name,
                          participant_score = p2_score,
                          opponent_name = participant_1_name,
                          opponent_score = p1_score,
                          win = p2_win,
                          loss = p1_win,
                          matches_id=current_match.id,
                          tournament_name = current_match.tournament_name,
                          tournament_trophy = 0,
                          stage  =current_match.stage,
                          date = current_match.date)

        output.append(get_match_by_id(current_match.id))
    return output




"GET TOURNAMENTS POINTS"
def get_participants_points_for_tournament(title: str):
    row_data = read_query('''SELECT player_name, player_score FROM players_statistics 
                                WHERE tournament_name = ?''',
                          (title,))
    result_dict = {}
    for name, score in row_data:
        if name in result_dict:
            result_dict[name] += score
        else:
            result_dict[name] = score

    return result_dict




# def finish_tournament(winner: str, t_title: str):
#     update_query('''UPDATE tournaments SET winner = ? WHERE title = ?''',
#                  (winner, t_title))
#     update_query('UPDATE players_statistics SET tournament_trophy = 1 WHERE player_name = ?',
#                  (winner, ))
#


    # for current_match in t_matches:
    #     participant_1 = player_service.get_player_by_full_name(current_match.participant_1)
    #     participant_2 = player_service.get_player_by_full_name(current_match.participant_2)
    #
    #     players = [1, 2]
    #     winner_id = random.choice(players)
    #     winner_name = participant_1.full_name if winner_id == 1 else participant_2.full_name
    #
    #     update_query('''UPDATE matches SET winner = ? WHERE id = ?''',
    #                  (winner_name, current_match.id))
    #
    #     # update players_statistics
    #     update_statistics(participant_1.id, participant_1.full_name,
    #                       participant_2.full_name,
    #                       win=1 if winner_id == 1 else 0,
    #                       loss=0 if winner_id == 1 else 1,
    #                       matches_id=current_match.id,
    #                       tournament_name=current_match.tournament_name,
    #                       date=current_match.date,
    #                       stage=current_match.stage)
    #
    #     update_statistics(participant_2.id, participant_2.full_name,
    #                       participant_1.full_name,
    #                       win=0 if winner_id == 1 else 1,
    #                       loss=1 if winner_id == 1 else 0,
    #                       matches_id=current_match.id,
    #                       tournament_name=current_match.tournament_name,
    #                       date=current_match.date,
    #                       stage=current_match.stage)
    #
    #     # update tournaments_players
    #     if current_match.tournament_name != 'not part of a tournament':
    #         t_title = current_match.tournament_name
    #         tournament_id = tournament_service.get_tournament_id_by_title(t_title)
    #         stage = int(current_match.stage) + 1
    #         insert_query('''INSERT INTO tournaments_players (players_id, player_name,
    #             tournaments_id, tournament_title, stage) VALUES (?, ?, ?, ?, ?)''',
    #                      (winner_id, winner_name, tournament_id, t_title, stage))
    #
    #         # prize for winner
    #         last = last_players(t_title)
    #         if len(last) == 1:
    #             finish_tournament(winner_name, t_title)