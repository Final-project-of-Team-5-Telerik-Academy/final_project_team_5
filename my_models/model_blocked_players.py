from pydantic import BaseModel


class Status:
    TEMPORARY = 'temporary'
    PERMANENT = 'permanent'
    
class BlockedPlayers(BaseModel):
    id: int
    players_id: int
    ban_status: str

    def is_temporary(self):
        ''' Shows that the status of the ban is temporary.
        
        Returns:
            - True/False
        '''

        return self.ban_status == Status.TEMPORARY
    
    def is_permanent(self):
        ''' Shows that the status of the ban is permanent.
        
        Returns:
            - True/False
        '''

        return self.ban_status == Status.PERMANENT

    @classmethod
    def from_query_result(cls, id, players_id, ban_status):
        ''' When query is used in another function.

        Returns:
            - id, players_id, ban_status
        '''
        return cls(id = id,
                   players_id = players_id,
                   ban_status = ban_status)