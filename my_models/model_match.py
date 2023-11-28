from pydantic import BaseModel, constr, conint
from datetime import date
from my_models.model_user import User

class Match(BaseModel):
    id: int | None
    match_format: constr(pattern='^time limit|score limit$')
    game_type: str
    sport: str
    participant_1: str
    participant_2: str
    creator: str
    date: date
    winner: str | None
    tournament_name: str | None
    stage: int


    @classmethod
    def from_query_result(cls, id, match_format, game_type, sport, participant_1, participant_2,
                          creator, date, winner, tournament_name, stage):
        return cls( id = id,
                    match_format = match_format,
                    game_type = game_type,
                    sport = sport,
                    participant_1 = participant_1,
                    participant_2 = participant_2,
                    creator = creator,
                    date = date,
                    winner = winner,
                    tournament_name = tournament_name,
                    stage = stage)


sports_list = [
    'football',
    'tennis'
]






