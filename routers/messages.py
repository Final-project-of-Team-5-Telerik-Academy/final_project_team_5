from fastapi import APIRouter, Header, Query
from services import message_service


messages_router = APIRouter(prefix='/messages', tags={'Messages'})


@messages_router.get('/', description='View all your conversations:')
def get_conversations(x_token: str = Header()):
    ''' Used for viewing all conversations of the user.
    
    Args:
        - JWT token(Query)
    
    Returns:
        - A list of all conversations
    '''

    return message_service.get_all_conversations(x_token)


@messages_router.get('/receiver_id', description='View conversation:')
def view_conversation(receiver_id: int = Query(..., description='Enter ID of the receiver:'), 
                      x_token: str = Header()):
    ''' Used for viewing a conversation. The conversation can be viewed by the sender and also by the receiver.
    
    Args:
        - receiver_id: int(Query)
        - JWT token(Query)
    
    Returns:
        - The whole conversation between the two user id's
    '''

    return message_service.view_conversation_by_ids(receiver_id, x_token)


@messages_router.post('/send/receiver_id', description='Send a new message:')
def send_new_message(message: str = Query(..., description='Message:'), 
                     receiver_id: int = Query(..., description='Enter ID of the receiver:'), 
                     x_token: str = Header()):
    ''' Used for sending a message to another user.
    
    Args:
        - message: str(Query)
        - receiver_id: int(Query)
        - JWT token(Query)
    
    Returns:
        - New Message
    '''

    return message_service.send_a_new_message(message, receiver_id, x_token)


@messages_router.put('/edit/id', description='Edit a message:')
def edit_message_by_id(new_message: str = Query(..., description='Edit message:'), 
                       id: int = Query(..., description='ID of the message:'), 
                       x_token: str = Header()):
    ''' Used for editing a message through id(of the message). Only the sender of the message can edit it.
    
    Args:
        - new_message: str(Query)
        - id(of the message): int(Query)
        - JWT token(Query)
    
    Returns:
        - Updated message
    '''

    return message_service.edit_message_by_id(new_message, id, x_token)


@messages_router.delete('/delete/id', description='Delete a message:')
def delete_message(id: int = Query(..., description='ID of the message:'), 
                   x_token: str = Header()):
    ''' Used for deleting a message through id(of the message). Only the sender of the message can delete it.
    
    Args:
        - id(of the message): int(Query)
        - JWT token(Query)
    
    Returns:
        - Deleted message
    '''

    return message_service.delete_message_by_id(id, x_token)