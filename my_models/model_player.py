from pydantic import BaseModel


class Player(BaseModel):
    id: int | None = None
    full_name: str
    country: str
    sports_club: str
    is_active: int | None = 0
    is_connected: int | None = 0
    teams_id: int | None = None

    @classmethod
    def from_query_result(cls, id, full_name, country, sports_club, is_active, is_connected, teams_id):
        ''' When query is used in another function.

        Returns:
            - id, full_name, country, sports_club, is_active, is_connected, teams_id
        '''

        return cls(
            id=id,
            full_name=full_name,
            country=country,
            sports_club=sports_club,
            is_active=is_active,
            is_connected=is_connected,
            teams_id=teams_id
        )
    