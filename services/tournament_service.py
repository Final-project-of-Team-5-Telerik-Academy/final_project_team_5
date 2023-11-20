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
                        participant = 'Add players/teams to the tournament')
    return result



def get_tournament_id_by_title(title: str):
    tournament_id = read_query('SELECT id FROM tournaments WHERE title = ?', (title,))
    return None if not tournament_id else tournament_id


def get_tournament_by_title(title: str):
    row_data = read_query('''SELECT id, title, format, date, prize, game_type, users_creator_id, is_finished 
        FROM tournaments WHERE title = ?''', (title,))

    data = row_data[0]
    id = data[0]
    title = data[1]
    format = data[2]
    date = data[3]
    prize = data[4]
    game_type = data[5]
    creator = data[6]
    is_finished = data[7]

    tournament = Tournament.from_query_result(*data)
    return tournament



def get_game_type(t_title):
    game_type = read_query(f'SELECT game_type FROM tournaments WHERE title = ?', (t_title,))
    result = game_type[0][0]
    return result

def add_participant(participant: Player, tournament: Tournament):   # TODO: add | Team
# add participant to the tournament instance
    tournament.participant.append(participant.id)

# add participant to tournaments_players table
    insert_query('''INSERT INTO tournaments_players (tournaments_id, players_id) 
                VALUES (?, ?)''', (tournament.id, participant.id))

    return f'{participant.full_name} joined the {tournament.title}'



def is_player_in_tournament(player_id: int, tournament_id: int):
    row_result = read_query('SELECT players_id FROM tournaments_players WHERE tournaments_id = ?',
                      (tournament_id, ))

    data = [el[0] for el in row_result]
    for el in data:
        if el == player_id:
            return True
    return False



# def view_tournament_participants(title: str):
#     # get all players for this tournament
#     all_players_id = read_query('''SELECT players_id FROM tournaments_players
#                                     WHERE tournaments_id = ?''', (tournament.id,))







    # result = {
    #     'id': f'{tournament.id}',
    #     'title': f'{tournament.title}',
    #     'format': f'{tournament.format}',
    #     'date': f'{tournament.date}',
    #     'prize': f'{tournament.prize}',
    #     'game type': f'{tournament.game_type}',
    #     'creator': f'{tournament.creator}',
    #     'is finished': f'{tournament.is_finished}',
    #     'players or teams': f'{tournament.participant}'}
    #
    # return result








