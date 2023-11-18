from pydantic import BaseModel, constr
from datetime import date

class Tournament(BaseModel):
    id: int | None
    title: str
    format: constr(pattern='^knockout|league$')
    date: date
    prize: int
    game_type: str
    creator: str
    is_finished: bool
    players_or_teams: list | str = None


    @classmethod
    def from_query_result(cls, id, title, format, date, prize, game_type,
                          creator, status, players_or_teams):
        return cls(id = id,
                   title = title,
                   format = format,
                   date = date,
                   prize = prize,
                   game_type = game_type,
                   creator = creator,
                   is_finished = status,
                   players_or_teams = players_or_teams)