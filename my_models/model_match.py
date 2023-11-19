from pydantic import BaseModel, constr, conint
from datetime import date
from my_models.model_user import User

class Match(BaseModel):
    id: int | None
    format: constr(pattern='^time limit|score limit$')
    participant_1: str
    participant_2: str
    date: date
    winner: str = None
    tournament_name: str = None


    @classmethod
    def from_query_result(cls, id, format, participant_1, participant_2,
                          date, winner, tournament_name):
        return cls( id = id,
                    format = format,
                    participant_1 = participant_1,
                    participant_2 = participant_2,
                    date = date,
                    winner = winner,
                    tournament_name = tournament_name)










