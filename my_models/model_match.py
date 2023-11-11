from pydantic import BaseModel, constr
from datetime import date


class Match(BaseModel):
    # FOR CREATING MATCH
    id: int | None
    date: date
    player_1: str   # TODO Player
    player_2: str   # TODO Player
    title: str
    format: constr(pattern='^knockout|league$')
    prize: int
    is_part_of_a_tournament: bool

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

