from data.database import insert_query, read_query
from my_models.model_match import Match
from my_models.model_user import User


def get_all_matches():
    data = read_query(f'''SELECT id, title, player_1, player_2, date, format, prize, is_part_of_a_tournament
             FROM match_score_db.matches"''')
    result = (Match.from_query_result(*row) for row in data)
    return result


def get_match_by_title(title: str):
    data = read_query(f'''SELECT id, title, player_1, player_2, date, format, prize, is_part_of_a_tournament
             FROM match_score_db.matches 
             WHERE title LIKE "%{title}%"''')
    result = (Match.from_query_result(*row) for row in data)
    return result



def get_sorted_matches(sort: str):
    if sort == 'ascending':
        sort = 'ASC'
    else:
        sort = "DESC"

    data = read_query(f'''SELECT id, title, player_1, player_2, date, format, prize, is_part_of_a_tournament
        FROM match_score_db.matches ORDERED BY title {sort}''')
    result = (Match.from_query_result(*row) for row in data)
    return result



def create_match(date: str,
                 title: str,
                 player_1: User,
                 player_2: User,
                 match_format: str,
                 prize: int,
                 creator: str,
                 tournament_name: str | None = None):
    generated_match = insert_query(
        '''INSERT INTO matches (title, player_1, player_2, date, format, prize, tournament_name, users_creator_id
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
        (date, title, player_1, player_2, match_format, prize, creator, tournament_name))



    result = Match(id=generated_match,
                   date = date,
                   title = title,
                   player_1 = player_1,
                   player_2 = player_2,
                   match_format = match_format,
                   prize = prize,
                   tournament_name = tournament_name,
                   creator = creator)
    return result