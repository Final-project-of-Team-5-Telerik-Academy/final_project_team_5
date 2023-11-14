from pydantic import BaseModel, constr
from datetime import date
from my_models.model_user import User

class Match(BaseModel):
    # FOR CREATING MATCH
    id: int | None
    date: date
    player_1: User
    player_2: User
    title: str
    format: constr(pattern='^knockout|league$')
    prize: int
    is_part_of_a_tournament: bool
    creator: User

    @classmethod
    def from_query_result(cls, id, date, player_1, player_2, title, format, prize, is_part_of_a_tournament ):
        return cls(id = id,
                   date = date,
                   player_1 = player_1,
                   player_2 = player_2,
                   title = title,
                   format = format,
                   prize = prize,
                   is_part_of_a_tournament = is_part_of_a_tournament)

