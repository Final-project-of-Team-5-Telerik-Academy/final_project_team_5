from pydantic import BaseModel


class DirectorRequests(BaseModel):
    id: int | None = None
    full_name: str
    country: str
    sports_club: str
    users_id: int
    status: str


    @classmethod
    def from_query_result(cls, id, full_name, country, sports_club, users_id, status):
        ''' When Admin Model request is shown in the response.
        
        Returns:
            - id, full_name, country, sports_club, users_id, status
        '''

        return cls(
            id=id,
            full_name=full_name,
            country=country,
            sports_club=sports_club,
            users_id=users_id,
            status=status
            )