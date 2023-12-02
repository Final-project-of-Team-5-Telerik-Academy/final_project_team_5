from data.database import insert_query, read_query, update_query
from fastapi.responses import JSONResponse
from datetime import date, timedelta
from my_models.model_user import User
from my_models.model_player import Player
from my_models.model_team import Team
from my_models.model_tournament import Tournament
from services import user_service, match_service, player_service, team_service
import random
from itertools import combinations



" 1. VIEW ALL TOURNAMENTS"
def get_tournaments(sort: str | None, status: str):
    sql = '''SELECT id, title, number_participants, t_format, match_format, sport, date, prize, 
    game_type, winner, users_creator_id, is_complete, stage FROM tournaments '''

    where_clause = []

    if status == 'played':
        where_clause.append('WHERE winner <> "Not finished yet"')
    elif status == 'upcoming':
        where_clause.append(f'WHERE winner = "Not finished yet"')

    where_clause.append(f'ORDER BY date {sort}')
    sql += ' '.join(where_clause)
    row_data = read_query(sql)

    if len(list(row_data)) == 0:
        return {'message': f'No tournaments for now.'}

    return (Tournament.from_query_result(*row) for row in row_data)




" 2. VIEW TOURNAMENT BY TITLE"
def get_tournament_by_title(title: str) -> Tournament | None:
    row_data = read_query('''SELECT id, title, number_participants, t_format, match_format,
        sport, date, prize, game_type, winner, users_creator_id, is_complete, stage 
        FROM tournaments WHERE title = ?''', (title,))

    if not row_data:
        return None
    tournament = Tournament.from_query_result(*row_data[0])
    return tournament





" 3. CREATE TOURNAMENT"
def create_tournament(title: str, number_participants: int, t_format: str, match_format: str,
                      sport: str, date: date, prize: int, game_type: str, creator: User, stage = 0):
    winner = 'Not finished yet'

    generated_tournament = insert_query('''INSERT INTO tournaments (title, number_participants, 
        t_format, match_format, sport, date, prize, game_type, winner, users_creator_id, stage)
        VALUE (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
        (title, number_participants, t_format, match_format, sport, date, prize, game_type, winner, creator.id, stage))

    id = generated_tournament
    creator_name = creator.full_name
    is_complete = False

    tournament = Tournament.from_query_result(id, title, number_participants,
        t_format, match_format, sport, date, prize, game_type, winner, creator_name, is_complete, stage)

    return tournament




def add_player_to_tournament(player: Player, tournament: Tournament, stage=0):
    insert_query('''INSERT INTO tournaments_players (players_id, player_name, tournaments_id, tournaments_title, stage) 
                VALUES (?, ?, ?, ?, ?)''', (player.id, player.full_name, tournament.id, tournament.title, stage))

    return {'message': f'{player.full_name} joined the {tournament.title}'}



def add_team_to_tournament(team: Team, tournament: Tournament, stage=0):
    insert_query('''INSERT INTO tournaments_teams (teams_id, teams_name, tournaments_id, tournaments_title, stage) 
                VALUES (?, ?, ?, ?, ?)''', (team.id, team.team_name, tournament.id, tournament.title, stage))
    return {'message': f'{team.team_name} joined the {tournament.title}'}



def is_player_in_tournament(player_id: int, tournament_id: int, table: str):
    row_result = read_query(f'SELECT {table}_id FROM tournaments_{table} WHERE tournaments_id = ?',
                      (tournament_id, ))

    data = [el[0] for el in row_result]
    for el in data:
        if el == player_id:
            return True
    return False



def get_participants(tournament: Tournament, stage: int | None = None):
    participants = []
    if tournament.game_type == 'one on one':
        sql = f'''SELECT p.id, p.full_name, p.country, p.sports_club FROM players p
        LEFT JOIN tournaments_players tp ON p.id = tp.players_id 
        WHERE tp.tournaments_id = {tournament.id}'''

        if stage:
            where_clause = f' AND tp.stage = {stage}'
            sql.join(where_clause)

        players_data = read_query(sql)
        for row in players_data:
            participants.append({'id': row[0],
                                 'name': row[1],
                                 'country': row[2],
                                 'sports club': row[3]})

    elif tournament.game_type == 'team game':
        teams_data = read_query('''SELECT teams.id, teams.team_name FROM teams
                                    LEFT JOIN tournaments_teams tt ON tt.teams_id = teams.id
                                    WHERE tt.tournaments_id = ?''', (tournament.id,))

        for row in teams_data:
            participants.append({'id': row[0], 'name': row[1]})

    return participants



def delete_tournament_by_title(title: str, game_type: str):
    if game_type == 'one on one':
        update_query('DELETE FROM tournaments_players WHERE tournaments_title = ?', (title,))
        update_query('DELETE FROM players_statistics WHERE tournament_name = ?', (title,))
    elif game_type == 'team game':
        update_query('DELETE FROM tournaments_teams WHERE tournaments_title = ?', (title,))
        update_query('DELETE FROM teams_statistics WHERE tournament_name = ?', (title,))

    update_query('DELETE FROM tournaments WHERE title = ?', (title,))
    update_query('DELETE FROM matches WHERE tournament_name = ?', (title,))



def enough_participants(tournament: Tournament):
    all_participants = get_participants(tournament)
    difference = tournament.number_participants - len(all_participants)
    if difference == 0:
        return JSONResponse(status_code=400,
                            content=f'The tournament allows only {tournament.number_participants} participants. You have enough.')


def need_or_complete(tournament: Tournament, table: str):
    all_participants = get_participants(tournament)
    difference = tournament.number_participants - len(all_participants)
    if difference > 0:
        return {'message': f'you need {difference} participants to complete the tournament.'}

    elif difference == 0:
        update_query('UPDATE tournaments SET is_complete = 1 WHERE title = ?',
                     (tournament.title,))
        return {'message': f'{tournament.title} is ready to begin.'}





" 6. ARRANGE TOURNAMENT KNOCKOUT MATCHES"
def create_knockout_stage(tournament: Tournament):
    participants_list = get_participants(tournament, tournament.stage)
    number_matches = len(participants_list) // 2

# set next tournament stage
    update_query('UPDATE tournaments SET stage = ? WHERE title = ?',
                 (tournament.stage + 1, tournament.title))

    stage = 0
    output = []
    for t_match in range(1, number_matches + 1):
    # choose participants
        participant_1 = random.choice(participants_list)
        participant_1_name = participant_1['name']
        participants_list.remove(participant_1)

        participant_2 = random.choice(participants_list)
        participant_2_name = participant_2['name']
        participants_list.remove(participant_2)
    # set a match
        match_format = tournament.match_format
        game_type = tournament.game_type
        sport = tournament.sport
        creator_name = user_service.get_user_full_name_by_id(tournament.creator)
        stage_date = tournament.date + timedelta(days=1)
        t_title = tournament.title
        stage = tournament.stage + 1

        match = match_service.create_match(match_format, game_type, sport, participant_1_name,
                               participant_2_name, creator_name, stage_date, t_title, stage)
        output.append(match)

# update match participants stage
    table = participant_type(tournament)
    update_query(f'UPDATE tournaments_{table}s SET stage = ? WHERE tournaments_title = ?',
                 (stage, tournament.title,))
    return output




" 6.2. ARRANGE TOURNAMENT LEAGUE MATCHES"
def arrange_league(tournament: Tournament, matches_per_days: int):
    participants_list = get_participants(tournament)
    unique_pairs = list(combinations(participants_list, 2))

    matches_list = []
    counter_matches = 0
    days_counter = 0

    for el in unique_pairs:
        participant_1 = el[0]
        participant_2 = el[1]

        match_format = tournament.match_format
        game_type = tournament.game_type
        sport = tournament.sport
        creator_name = user_service.get_user_full_name_by_id(tournament.creator)
        t_title = tournament.title

        if counter_matches % matches_per_days == 0:
            days_counter += 1
        date = tournament.date + timedelta(days=days_counter)

        match = match_service.create_match(match_format = match_format,
                                           game_type = game_type,
                                           sport = sport,
                                           participant_1 = participant_1['name'],
                                           participant_2 = participant_2['name'],
                                           creator_name = creator_name,
                                           date = date,
                                           t_title = t_title,
                                           stage = tournament.stage)
        counter_matches += 1
        matches_list.append(match)
    return matches_list




" 6.1. SIMULATE  KNOCKOUT TOURNAMENT"
def simulate_knockout_tournament_matches(tournament: Tournament):
    all_matches = match_service.get_knockout_matches_by_tournament(tournament.title, tournament.stage)


    output = []
    output.append('-= KNOCKOUT TOURNAMENT SIMULATIONS RESULTS =-')
    for current_match in all_matches:
        if current_match.tournament_name == "not part of a tournament":
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

        if p1_score >= p2_score:
            winner_name = participant_1_name
            p1_win = 1
            p2_win = 0
            p2_score -= 1
            level_participants_stage(p_type, tournament.title, winner_name, tournament.stage + 1)
        else:
            winner_name = participant_2_name
            p1_win = 0
            p2_win = 1
            level_participants_stage(p_type, tournament.title, winner_name, tournament.stage + 1)

        update_query('''UPDATE matches SET winner = ? WHERE id = ?''',
                     (winner_name, current_match.id))

        match_service.update_statistics(p_type=p_type,
                                        participant_id=participant_1.id,
                                        participant_name=participant_1_name,
                                        participant_score=p1_score,
                                        opponent_name=participant_2_name,
                                        opponent_score=p2_score,
                                        win=p1_win,
                                        loss=p2_win,
                                        matches_id=current_match.id,
                                        tournament_name=current_match.tournament_name,
                                        tournament_trophy=0,
                                        stage=current_match.stage,
                                        date=current_match.date)

        match_service.update_statistics(p_type=p_type,
                                        participant_id=participant_2.id,
                                        participant_name=participant_2_name,
                                        participant_score=p2_score,
                                        opponent_name=participant_1_name,
                                        opponent_score=p1_score,
                                        win=p2_win,
                                        loss=p1_win,
                                        matches_id=current_match.id,
                                        tournament_name=current_match.tournament_name,
                                        tournament_trophy=0,
                                        stage=current_match.stage,
                                        date=current_match.date)

        output.append(match_service.get_match_by_id(current_match.id))

    new_stage = tournament.stage + 1
    update_query(f'UPDATE tournaments SET stage = ? WHERE tournaments_title = ?',
                 (new_stage, tournament.title,))
    return output



def level_participants_stage(table: str, title: str, winner: str, stage: int):
    update_query(f'''UPDATE tournaments_{table}s SET stage = ?
                    WHERE tournaments_title = ? AND {table}_name = ?''',
                 (stage, title, winner))





"GET TOURNAMENTS POINTS"
def get_league_participants_points_for_tournament(tournament: Tournament):
    participants_list = get_participants(tournament)

    all_results = []
    for el in participants_list:
        participant_name = el['name']

        if tournament.game_type == 'one on one':
            row_data = read_query('''SELECT player_score FROM players_statistics 
                                        WHERE tournament_name = ? AND player_name = ?''',
                                  (tournament.title, participant_name))
        else:   # team game
            row_data = read_query('''SELECT team_score FROM teams_statistics 
                                        WHERE tournament_name = ? AND team_name = ?''',
                                  (tournament.title, participant_name))

        score = 0
        for num in row_data:
            score += num[0]

        result_dict = {round(score, 2) : participant_name}
        all_results.append(result_dict)

    sorted_list = sorted(all_results, key=lambda d: list(d.keys())[0])
    return sorted_list


"ADD TOURNAMENT TROPHY"
def add_tournament_trophy(participant: str, p_type: str, t_title: str):
    match_id_list = read_query(f'''SELECT matches_id FROM {p_type}s_statistics 
                    WHERE {p_type}_name = ? AND tournament_name = ?''',
                    (participant, t_title))
    max_id = 0
    for el in match_id_list:
        num = el[0]
        if max_id < num:
            max_id = num

    tournaments_trophy_data = read_query(f'''SELECT tournament_trophy FROM {p_type}s_statistics 
                                            WHERE {p_type}_name = ?''',(participant,))
    tournaments_trophy = sum([el[0] for el in tournaments_trophy_data])

    trophies = tournaments_trophy + 1
    add_trophy = update_query(f'''UPDATE {p_type}s_statistics SET tournament_trophy = ? 
        WHERE matches_id = ? AND {p_type}_name = ?''', (trophies, max_id, participant))



"SET TOURNAMENTS WINNER @ TOURNAMENTS TABLE"
def set_winner(title: str, winner: str):
    update_query('UPDATE tournaments SET winner = ? WHERE title = ?',
                 (winner, title))


def has_winner(title: str):
    row_data = read_query('SELECT winner FROM tournaments WHERE title = ?',
                          (title,))

    return row_data[0][0]


def participant_type(tournament: Tournament):
    if tournament.game_type == 'one on one':
        t_table = 'player'
    else:
        t_table = 'team'
    return t_table