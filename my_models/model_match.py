from pydantic import BaseModel, constr, conint
from datetime import date
from my_models.model_user import User

class Match(BaseModel):
    # FOR CREATING MATCH
    id: int | None
    title: str = None
    date: date
    player_1: str | list = []
    player_2: str | list = []
    match_format: constr(pattern='^time limit|score limit$')
    prize: conint(gt=-1) = 0
    tournament_name: str = None
    creator: str = None
    played: bool = False
    winner: str = None

    @classmethod
    def from_query_result(cls, id, date, player_1, player_2, title, format, prize, is_part_of_a_tournament,played, winner ):
        return cls(id = id,
                   date = date,
                   player_1 = player_1,
                   player_2 = player_2,
                   title = title,
                   format = format,
                   prize = prize,
                   is_part_of_a_tournament = is_part_of_a_tournament,
                   played=played,
                   winner=winner)

