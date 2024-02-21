from pydantic import BaseModel, constr
from datetime import datetime


class Message(BaseModel):
    id: int | None = None
    content: constr(min_length=2, max_length=250)
    timestamp: datetime | None = None
    sender_id: int | None = None
    receiver_id: int | None = None


class MessageResponseModel(BaseModel):
    id: int | None = None
    content: constr(min_length=2, max_length=250)
    timestamp: datetime | None = None
    sender_id : int | None = None
    receiver_id: int | None = None
    

    @classmethod
    def from_query_result(cls, id, content, timestamp, sender_id, receiver_id):
        ''' When MessageResponseModel is shown in the response.
        
        Returns:
            - id, content, timestamp, sender_id, receiver_id
        '''
        
        return cls(
                    id=id,
                    content=content,
                    timestamp=timestamp,
                    sender_id=sender_id,
                    receiver_id=receiver_id
        )


# class CreateMessageModel(BaseModel):
#     id: int | None = None
#     content: constr(min_length=2, max_length=250)
#     timestamp: datetime | None = None