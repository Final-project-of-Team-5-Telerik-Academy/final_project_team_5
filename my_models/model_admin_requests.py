from pydantic import BaseModel, constr

class AdminRequests(BaseModel):
    id: int | None
    type_of_request: str    
    players_id: int
    users_id: int
