from pydantic import BaseModel
from my_models.model_player import Player


class Team(BaseModel):
    id: int | None = None
    team_name: str
    number_of_players: int | None = 0
    owners_id: int | None = None
    players: list[Player] = []


    @classmethod
    def from_query_result(cls, id, team_name, number_of_players, owners_id):
        ''' When query is used in another function.
        
        Returns:
            - id, team_name, number_of_players, owners_id
        '''

        return cls(
            id=id,
            team_name=team_name,
            number_of_players=number_of_players,
            owners_id=owners_id
            )
    
    
    @classmethod
    def from_query_result_additional(cls, team_data):
        ''' When query is used in another function.
        
        Returns:
            - id, team_name, number_of_players, owners_id
        '''

        return cls(
            id=team_data[0],
            team_name=team_data[1],
            number_of_players=team_data[2],
            owners_id=team_data[3]
            )
