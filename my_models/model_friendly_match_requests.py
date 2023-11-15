from pydantic import BaseModel

class FriendlyMatchRequests(BaseModel):
    id: int | None = None
    messsage: str | None = None
    sender_id: int
    receiver_id: int
    status: str | None = None

    @classmethod
    def from_query_result(cls, id, message, sender_id, receiver_id, status):
        ''' When FriendlyMatchRequests Model is shown in the response.
        
        Returns:
            - id, message, sender_id, receiver_id, status
        '''

        return cls(
            id=id,
            message=message,
            sender_id=sender_id,
            receiver_id=receiver_id,
            status=status
            )
