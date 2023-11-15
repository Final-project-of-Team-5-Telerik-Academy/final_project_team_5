from my_models.model_player import Player
from data.database import read_query


def player_exists(name):
    pass


def create_uncompleted_player(name):
    pass

def get_player_by_id(players_id: int) -> Player | None:

    data = read_query(
        'SELECT id, full_name, country, sport_club, audience_vote, points, titles, wins, losses, money_prize, is_injured, is_active, statistics_matches_id FROM players WHERE id = ?',
        (players_id,)
        )

    return next((Player.from_query_result(*row) for row in data), None)