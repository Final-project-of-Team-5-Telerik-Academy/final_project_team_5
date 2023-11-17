from pydantic import BaseModel

class TypeOfRequests:
    CONNECTION = 'connection'
    PROMOTION = 'promotion'

class AdminRequests(BaseModel):
    id: int | None
    type_of_request: str    
    players_id: int
    users_id: int
    status: str

    def is_connected(self):
        ''' Compares the request's type of the request.
        
        Returns:
            - True/False
        '''

        return self.type_of_request == TypeOfRequests.CONNECTION
    
    
    def is_promoted(self):
        ''' Compares the request's type of the request.
        
        Returns:
            - True/False
        '''

        return self.type_of_request == TypeOfRequests.PROMOTION
    

    @classmethod
    def from_query_result(cls, id, type_of_request, players_id, users_id, status):
        ''' When Admin Model request is shown in the response.
        
        Returns:
            - id, type_of_request, players_id, users_id, status
        '''

        return cls(
            id=id,
            type_of_request=type_of_request,
            players_id=players_id,
            users_id=users_id,
            status=status
            )
