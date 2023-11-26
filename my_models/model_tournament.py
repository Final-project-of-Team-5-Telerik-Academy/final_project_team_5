from pydantic import BaseModel, constr
from datetime import date
from services import user_service


class Tournament(BaseModel):
    id: int | None
    title: str
    number_participants: int
    t_format: constr(pattern='^knockout|league$')
    match_format: constr(pattern='time limit|score limit$')
    date: date
    prize: int
    game_type: str
    winner: str | None
    creator: str | int
    is_complete: str | bool
    stage: int

    @classmethod
    def from_query_result(cls, id, title, number_participants, t_format, match_format, date,
                          prize, game_type, winner, creator, is_complete, stage):

        result =cls(id = id,
                    title = title,
                    number_participants = number_participants,
                    t_format = t_format,
                    match_format = match_format,
                    date = date,
                    prize = prize,
                    game_type = game_type,
                    winner = winner,
                    creator = creator,
                    is_complete = is_complete,
                    stage = stage)
        return result



