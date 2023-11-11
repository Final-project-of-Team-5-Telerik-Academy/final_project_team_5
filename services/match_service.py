from data.database import insert_query, read_query, update_query
from my_models.model_match import Match


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



def create_match(match: Match):
    generated_match = insert_query()
    pass