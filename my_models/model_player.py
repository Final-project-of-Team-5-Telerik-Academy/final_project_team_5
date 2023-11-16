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
    statistics_matches_id: int | None = None

    @classmethod
    def from_query_result(cls, id, full_name, country, sport_club, audience_vote, points, titles, wins, losses, money_prize, is_injured, is_active, statistics_matches_id):
        ''' When query is used in another function.
        
        Returns:
            - id, full_name, country, sport_club, audience_vote, points, titles, wins, losses, money_prize, is_injured, is_active, statistics_matches_id
        '''

        return cls(
            id=id,
            full_name=full_name,
            country=country,
            sport_club=sport_club,
            audience_vote=audience_vote,
            points=points,
            titles=titles,
            wins=wins,
            losses=losses,
            money_prize=money_prize,
            is_injured=is_injured,
            is_active=is_active,
            statistics_matches_id=statistics_matches_id
            )