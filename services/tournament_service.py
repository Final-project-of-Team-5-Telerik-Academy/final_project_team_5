from data.database import insert_query, read_query, update_query
from fastapi.responses import JSONResponse
from datetime import date, timedelta
from my_models.model_user import User
from my_models.model_player import Player
from my_models.model_team import Team
from my_models.model_tournament import Tournament
from services import date_service, user_service, match_service, date_service
import random



def create_tournament(title: str, number_participants: int, t_format: str, match_format: str,
                      date: date, prize: int, game_type: str, creator: User, stage = 0):
    winner = 'Not finished yet'
    generated_tournament = insert_query('''INSERT INTO tournaments (title, number_participants, 
        t_format, match_format, date, prize, game_type, winner, users_creator_id, stage)
        VALUE (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
        (title, number_participants, t_format, match_format, date, prize, game_type, winner, creator.id, stage))

    id = generated_tournament
    title = title
    number_participants = number_participants
    t_format = t_format
    match_format = match_format
    date = date
    prize = prize
    game_type = game_type
    winner = winner
    creator = creator.full_name
    is_complete = False
    stage = stage

    tournament = Tournament.from_query_result(id, title, number_participants,
        t_format, match_format, date, prize, game_type, winner, creator, is_complete, stage)

    return tournament



def get_tournament_id_by_title(title: str):
    tournament_id = read_query('SELECT id FROM tournaments WHERE title = ?', (title,))
    return None if not tournament_id else tournament_id[0][0]



def get_tournament_by_title(title: str):
    row_data = read_query('''SELECT id, title, number_participants, t_format, match_format,
        date, prize, game_type, winner, users_creator_id, is_complete, stage 
        FROM tournaments WHERE title = ?''', (title,))

    if not row_data:
        return None
    tournament = Tournament.from_query_result(*row_data[0])
    return tournament



def get_game_type(t_title):
    game_type = read_query(f'SELECT game_type FROM tournaments WHERE title = ?', (t_title,))
    result = game_type[0][0]
    return result



def add_player(player: Player, tournament: Tournament):
    insert_query('''INSERT INTO tournaments_players (players_id, player_name, tournaments_id, tournament_title) 
                VALUES (?, ?, ?, ?)''', (player.id, player.full_name, tournament.id, tournament.title))

    return f'{player.full_name} joined the {tournament.title}'



def add_team(team: Team, tournament: Tournament):
    insert_query('''INSERT INTO tournaments_teams (teams_id, teams_name, tournaments_id, tournament_title) 
                VALUES (?, ?, ?, ?)''', (team.id, team.team_name, tournament.id, tournament.title))

    return f'{team.full_name} joined the {tournament.title}'



def is_player_in_tournament(player_id: int, tournament_id: int):
    row_result = read_query('SELECT players_id FROM tournaments_players WHERE tournaments_id = ?',
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
            participants.append({'id': row[0], 'name': row[1], 'country': row[2], 'sports club': row[3]})



    elif tournament.game_type == 'team game':
        teams_data = read_query('''SELECT t.id, t.team_name FROM teams t 
                                    LEFT JOIN tournaments_teams tp ON p.id = tp.players_id
                                    WHERE tp.tournaments_id = ?''', (tournament.id,))
        for row in teams_data:
            participants.append({'id': row[0], 'name': row[1]})

    return participants




def get_tournaments(sort: str | None, status: str):
    sql = '''SELECT id, title, number_participants, t_format, match_format, date, prize, 
    game_type, winner, users_creator_id, is_complete, stage FROM tournaments '''
    today = date_service.current_date()
    where_clause = []

    if status == 'played':
        where_clause.append('WHERE winner <> "Not finished yet"')
    elif status == 'upcoming':
        where_clause.append(f"WHERE date > '{today}'")

    where_clause.append(f'ORDER BY date {sort}')
    sql += ' '.join(where_clause)
    row_data = read_query(sql)

    if status == len(list(row_data)) == 0:
        return f'No tournaments for now.'

    result = []
    for el in row_data:
        if el[8] == 1:
            id = el[0]
            title = el[1]
            number_participant = el[2]
            t_format = el[3]
            match_format = el[4]
            date = el[5]
            prize = el[6]
            game_type = el[7]
            winner = 'Not finished yet' if el[8] is None else el[8]
            creator = user_service.get_user_full_name_by_id(el[9])
            is_complete = True if el[10] == 1 else False
            stage = el[11]
            tournament = Tournament.from_query_result(id, title, number_participant, t_format,
                match_format, date,prize, game_type, winner, creator, is_complete, stage)

            result.append(tournament)

    return result



def complete_tournament(tournament_title: str):
    update_query('UPDATE match_score_db.tournaments SET is_complete = 1, stage = 1 WHERE title = ?',
                 (tournament_title, ))



def delete_tournament_by_title(title: str, game_type: str):
    if game_type == 'one on one':
        update_query('DELETE FROM tournaments_players WHERE tournament_title = ?', (title,))
    elif game_type == 'team game':
        update_query('DELETE FROM tournaments_teams WHERE tournament_title = ?', (title,))
    update_query('DELETE FROM tournaments WHERE title = ?', (title,))



def enough_participants(tournament: Tournament):
    participants = get_participant(tournament)
    difference = tournament.number_participants - len(participants)
    if difference <= 0:
        return True


def get_unfinished_tournaments() -> list[Tournament] | None:
    row_data = read_query(sql = '''SELECT id, title, number_participants, t_format, 
    match_format, date, prize, game_type, winner, users_creator_id, is_complete, stage 
    FROM tournaments WHERE winner = "Not finished yet"''')

    result = []
    for el in row_data:
        if el[8] == 'Not finished yet' and el[10] == 1:
            id = el[0]
            title = el[1]
            number_participant = el[2]
            t_format = el[3]
            match_format = el[4]
            date = el[5]
            prize = el[6]
            game_type = el[7]
            winner = 'Not finished yet' if el[8] is None else el[8]
            creator = user_service.get_user_full_name_by_id(el[9])
            is_complete = True if el[10] == 1 else False
            stage = el[11]
            tournament = Tournament.from_query_result(id, title, number_participant, t_format,
                match_format, date, prize, game_type, winner, creator, is_complete, stage)
            result.append(tournament)

    if len(result) == 0:
        return None
    return result




"=== PLAY TOURNAMENT ==="

def tournaments_stage():
    all_tournaments = get_unfinished_tournaments()
    list_len = len(all_tournaments)
    for i in range(list_len):
        tournament = all_tournaments[i]

        participants_list = get_participant(tournament, tournament.stage)
        number_matches = len(participants_list) // 2
        for t_match in range(1, number_matches + 1):

            participant_1 = random.choice(participants_list)
            participant_1_name = participant_1['name']
            participants_list.remove(participant_1)

            participant_2 = random.choice(participants_list)
            participant_2_name = participant_2['name']
            participants_list.remove(participant_2)
        # set a match
            match_format = tournament.match_format
            game_type = tournament.game_type
            stage_date = tournament.date + timedelta(days=1)
            t_title = tournament.title
            current_stage = tournament.stage
            stage = current_stage
            match = match_service.create_match(match_format, game_type, participant_1_name,
                                   participant_2_name, stage_date, t_title, stage)

            # update_player_stage(participant_1, participant_1.stage)
            # update_player_stage(participant_2, participant_2.stage)

        new_stage = int(tournament.stage) + 1
        title = tournament.title
        update_query('UPDATE tournaments SET stage = ? WHERE title = ?',
                     (new_stage, title))






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


