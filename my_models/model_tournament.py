from pydantic import BaseModel, constr
from datetime import date
from services import user_service


class Tournament(BaseModel):
    id: int | None
    title: str
    format: constr(pattern='^knockout|league$')
    date: date
    prize: int
    game_type: str
    creator: str | int
    is_finished: bool
    participant: list | str = None


    @classmethod
    def from_query_result(cls, id, title, format, date, prize,
                          game_type, creator_id, is_finished):

        creator_name = user_service.get_user_full_name_by_id(creator_id)
        pt_list = []
        return cls(id = id,
                   title = title,
                   format = format,
                   date = date,
                   prize = prize,
                   game_type = game_type,
                   creator = creator_name,
                   is_finished = is_finished,
                   participant = pt_list)


