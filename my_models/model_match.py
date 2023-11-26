from pydantic import BaseModel, constr, conint
from datetime import date
from my_models.model_user import User

class Match(BaseModel):
    id: int | None
    format: constr(pattern='^time limit|score limit$')
    game_type: str
    participant_1: str
    participant_2: str
    date: date
    winner: str | None = None
    tournament_name: str | None = None
    stage: int | None = None


    @classmethod
    def from_query_result(cls, id, format, game_type, participant_1, participant_2,
                          date, winner, tournament_name, stage):
        return cls( id = id,
                    format = format,
                    game_type = game_type,
                    participant_1 = participant_1,
                    participant_2 = participant_2,
                    date = date,
                    winner = winner,
                    tournament_name = tournament_name,
                    stage = stage)









