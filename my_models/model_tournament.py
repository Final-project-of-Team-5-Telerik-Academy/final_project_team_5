from pydantic import BaseModel, constr
from datetime import date
from services import user_service


class Tournament(BaseModel):
    id: int | None
    title: str
    number_participants: int
    format: constr(pattern='^knockout|league$')
    date: date
    prize: int
    game_type: str
    winner: str | None
    creator: str | int
    is_complete: str | bool
    stage: int

    @classmethod
    def from_query_result(cls, id, title, number_participants, format, date,
                          prize, game_type, winner, creator, is_complete, stage):

        # creator_name = user_service.get_user_full_name_by_id(creator_id)
        result =cls(id = id,
                    title = title,
                    number_participants = number_participants,
                    format = format,
                    date = date,
                    prize = prize,
                    game_type = game_type,
                    winner = winner,
                    creator = creator,
                    is_complete = is_complete,
                    stage = stage)
        return result



