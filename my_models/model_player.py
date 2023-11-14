from pydantic import BaseModel

class Player(BaseModel):
    id: int | None = None
    full_name: str
    country: str
    sport_club: str
    audience_vote: int | None = 0
    points: int | None = 0
    titles: int | None = 0
    wins: int | None = 0  
    losses: int | None = 0
    money_prize: int = 0
    is_injured: int | None = 0
    is_active: int | None = 1
    statistic_matches_id: int | None = None

