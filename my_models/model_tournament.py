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
    def from_query_result(cls, id: int, title: str, number_participants: int, t_format: str,
                          match_format: str, date, prize, game_type, winner, creator: str, is_complete, stage):

        # creator_name = user_service.get_user_full_name_by_id(creator)
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
                    is_complete = False if is_complete == 0 else True,
                    stage = stage)
        return result



