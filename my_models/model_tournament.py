from pydantic import BaseModel, constr


class Tournament(BaseModel):
    id: int | None
    title: str
    format: constr(pattern='^knockout|league$')
    date: str
    prize: int
    players: list = []
    creator: str

    @classmethod
    def from_query_result(cls, id, title, format, date, prize):
        return cls(id = id,
                   title = title,
                   format = format,
                   date = date,
                   prize = prize)