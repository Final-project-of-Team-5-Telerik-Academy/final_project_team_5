from data.database import insert_query, read_query, update_query
from fastapi.responses import JSONResponse
from datetime import date, timedelta
from my_models.model_user import User
from my_models.model_player import Player
from my_models.model_team import Team
from my_models.model_tournament import Tournament
from services import date_service, user_service, match_service, date_service
import random



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




def add_player_to_tournament(player: Player, tournament: Tournament):
    insert_query('''INSERT INTO tournaments_players (players_id, player_name, tournaments_id, tournaments_title) 
                VALUES (?, ?, ?, ?)''', (player.id, player.full_name, tournament.id, tournament.title))

    return {'message': f'{player.full_name} joined the {tournament.title}'}



def add_team(team: Team, tournament: Tournament):
    insert_query('''INSERT INTO tournaments_teams (teams_id, teams_name, tournaments_id, tournaments_title) 
                VALUES (?, ?, ?, ?)''', (team.id, team.team_name, tournament.id, tournament.title))
    return {'message': f'{team.team_name} joined the {tournament.title}'}



def is_player_in_tournament(player_id: int, tournament_id: int, table: str):
    row_result = read_query(f'SELECT {table}_id FROM tournaments_{table} WHERE tournaments_id = ?',
                      (tournament_id, ))

    data = [el[0] for el in row_result]
    for el in data:
        if el == player_id:
            return True
    return False



def get_participant(tournament: Tournament, stage: int | None = None):
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
        teams_data = read_query('''SELECT t.id, t.team_name FROM teams t 
                                    LEFT JOIN tournaments_teams tp ON p.id = tp.players_id
                                    WHERE tp.tournaments_id = ?''', (tournament.id,))
        for row in teams_data:
            participants.append({'id': row[0], 'name': row[1]})

    return participants



def delete_tournament_by_title(title: str, game_type: str):
    if game_type == 'one on one':
        update_query('DELETE FROM tournaments_players WHERE tournaments_title = ?', (title,))
    elif game_type == 'team game':
        update_query('DELETE FROM tournaments_teams WHERE tournaments_title = ?', (title,))
    update_query('DELETE FROM tournaments WHERE title = ?', (title,))



def enough_participants(tournament: Tournament):
    all_participants = get_participant(tournament)
    difference = tournament.number_participants - len(all_participants)
    if difference == 0:
        return JSONResponse(status_code=400,
                            content=f'The tournament allows only {tournament.number_participants} participants. You have enough.')


def need_or_complete(tournament: Tournament, table: str):
    all_participants = get_participant(tournament)
    difference = tournament.number_participants - len(all_participants)
    if difference > 0:
        return {'message': f'you need {difference} participants to complete the tournament.'}

    elif difference == 0:
        update_query('UPDATE tournaments SET is_complete = 1, stage = 1 WHERE title = ?',
                     (tournament.title,))
        update_query(f'UPDATE tournaments_{table} SET stage = 1 WHERE tournaments_title = ?',
                     (tournament.title,))
        return {'message': f'{tournament.title} is ready to begin.'}





" 6. CREATE STAGE"
def create_stage(tournament: Tournament):
    participants_list = get_participant(tournament, tournament.stage)
    number_matches = len(participants_list) // 2

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
        stage = tournament.stage

        match = match_service.create_match(match_format, game_type, sport, participant_1_name,
                               participant_2_name, creator_name, stage_date, t_title, stage)
        output.append(match)


    new_stage = int(tournament.stage) + 1
    title = tournament.title
    update_query('UPDATE tournaments SET stage = ? WHERE title = ?',
                 (new_stage, title))

    return output







# number_matches = int(tournament.number_participants // 2)
# for t_match in range(1, number_matches + 1):
#     participants_list = get_participant(tournament, tournament.stage)
#
#     participant_1 = random.choice(participants_list)
#     participant_1_name = participant_1['name']
#
#     participant_2 = random.choice(participants_list)
#     participant_2_name = participant_2['name']
#
#     # set a match
#     match_format = tournament.match_format
#     game_type = tournament.game_type
#     stage_date = tournament.date + timedelta(days=1)
#     t_title = tournament.title
#     current_stage = tournament.stage
#     stage = current_stage + 1
#     match = match_service.create_match(match_format, game_type, participant_1_name,
#                                        participant_2_name, stage_date, t_title, stage)
#
#     participants_list.remove(participant_1)
#     participants_list.remove(participant_2)
#
# current_stage = tournament.stage
# new_stage = current_stage + 1
# update_query(f'UPDATE tournaments SET stage = {new_stage} WHERE title = {tournament.title}')
#


