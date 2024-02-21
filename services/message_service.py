from datetime import datetime
from fastapi.responses import JSONResponse
from authentication.authenticator import get_user_or_raise_401
from data.database import insert_query, read_query, read_query_additional, update_query
from my_models.model_message import Message, MessageResponseModel


def all():
    ''' Used for getting all messages from database.

    Returns:
        - List of all messages
    '''

    messages = read_query_additional('''SELECT * FROM messages''')

    if messages:
        return (MessageResponseModel.from_query_result(*msg) for msg in messages)
    else:
        return JSONResponse(status_code=404, content='No messages found.')
    

def get_conversation(sender_id, receiver_id):
    ''' Used for getting the whole conversation between two users from the database.'''

    messages = read_query('''SELECT id, content, timestamp, sender_id, receiver_id FROM messages WHERE (sender_id = ? AND receiver_id = ?)
                           OR (sender_id = ? AND receiver_id = ?)
                           ORDER BY timestamp ASC''', (sender_id, receiver_id, receiver_id, sender_id))
    
    if messages:
        return [MessageResponseModel.from_query_result(*msg) for msg in messages]
    

def get_by_id(id: int):
    ''' Used for getting a message by message.id from a conversation between two users from the database.'''

    message = read_query_additional('''SELECT id, content, timestamp, sender_id, receiver_id from messages WHERE id = ?''', (id,))

    return MessageResponseModel.from_query_result(*message)
    

def get_conversations_list_sender(sender_id):
    ''' Used for getting all conversations of the user from the database.'''

    conversations = read_query('''SELECT receiver_id from messages WHERE sender_id = ?''', (sender_id,))
    
    return conversations


def get_conversations_list_receiver(sender_id):
    ''' Used for getting all conversations of the user from the database.'''

    conversations = read_query('''SELECT sender_id from messages WHERE receiver_id = ?''', (sender_id,))
    
    return conversations


def send_message(
        content: str,
        sender_id: int,
        receiver_id: int):
    ''' Used for saving a new message in a conversation in the database.'''

    DATETIME_NOW = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    generated_id = insert_query('''INSERT INTO messages(content, timestamp, sender_id, receiver_id) VALUES (?, ?, ?, ?)''',
                                (content, DATETIME_NOW, sender_id, receiver_id))

    message = Message(
        id=generated_id,
        content=content,
        timestamp=DATETIME_NOW,
        sender_id=sender_id,
        receiver_id=receiver_id
    )

    return message


def delete_message(id: int):
    ''' Used for deleting a message by message.id in a conversation in the database.'''

    insert_query('''DELETE FROM messages WHERE id = ?''',
                 (id,))


def edit_message(old_message: Message, new_message: str):
    ''' Used for editing a message by message.id in a conversation in the database.'''
    
    edited_message = Message(
        id=old_message.id,
        content=new_message,
        timestamp=old_message.timestamp,
        sender_id=old_message.sender_id,
        receiver_id=old_message.receiver_id
    )

    update_query('''UPDATE messages SET content = ? WHERE id= ?''', (edited_message.content, edited_message.id))

    return edited_message


def id_exists(id: int, table_name: str) -> bool:
    ''' Used to check if the id exists in the table in the database.'''

    return any(
        read_query(
            f'SELECT id FROM {table_name} where id = ?',
            (id,)))


def view_conversation_by_ids(receiver_id, x_token):
    if x_token == None:
            return JSONResponse(status_code=401, content='You need to log-in to send a message.')
    
    user = get_user_or_raise_401(x_token)

    if not id_exists(receiver_id, 'users'):
        return JSONResponse(status_code=404, content=f'Receiver with ID: {receiver_id} does not exist.')

    elif user.id == receiver_id:
        return JSONResponse(status_code=404, content=f'Receiver with ID: {receiver_id} does not exist.')
    
    all_messages = get_conversation(user.id, receiver_id)

    if all_messages == None:
        return f'You have no messages with user with ID: {receiver_id}.'

    return all_messages


def get_all_conversations(x_token):
    if x_token == None:
        return JSONResponse(status_code=401, content='You need to log-in to view conversations list.')
    
    user = get_user_or_raise_401(x_token)
    
    conversations_sender = get_conversations_list_sender(user.id)
    conversations_receiver = get_conversations_list_receiver(user.id)

    all_conversations = []

    for conversation_id in conversations_sender:
        all_conversations.append(conversation_id)

    for conversation_id in conversations_receiver:
        all_conversations.append(conversation_id)

    if not all_conversations:
        return 'You have no conversations.'
    
    all_conversations = set(all_conversations)

    all_conversations = list(all_conversations)
    
    conversations = ''
    
    for conversation in all_conversations:
        conversation = str(conversation).removeprefix('(')
        conversation = str(conversation).removesuffix(',)')
        conversations = conversations + str(conversation) + ', '

    conversations = conversations.removesuffix(', ')

    return f"You have conversations with receiver's id's: {conversations}"


def send_a_new_message(content, receiver_id, x_token):
    if x_token == None:
        return JSONResponse(status_code=401, content='You need to log-in to send a message.')
    
    user = get_user_or_raise_401(x_token)
   
    if not id_exists(receiver_id, 'users'):
        return JSONResponse(status_code=404, content=f'Receiver with ID: {receiver_id} does not exist.')
    
    elif user.id == receiver_id:
        return JSONResponse(status_code=400, content='You are trying to message yourself. Try a different receiver ID.')
    
    send_message(content, user.id, receiver_id)

    return {'Message sent.'}


def edit_message_by_id(new_message, id, x_token):
    if x_token == None:
        return JSONResponse(status_code=401, content='You need to log-in to edit your message.')
    
    user = get_user_or_raise_401(x_token)
    
    if not id_exists(id, 'messages'):
        return JSONResponse(status_code=404, content=f'Message with id {id} does not exist.')

    message = get_by_id(id)
    
    if message.sender_id != user.id:
        return JSONResponse(status_code=401, content='You are allowed to edit only your sent messages.')
    
    old_message = get_by_id(id)

    edit_message(old_message, new_message)

    return {'Message updated.'}


def delete_message_by_id(id, x_token):
    if x_token == None:
        return JSONResponse(status_code=401, content='You need to log-in to delete your message.')  
    
    elif not id_exists(id, 'messages'):
        return JSONResponse(status_code=404, content=f'Message with id {id} does not exist.') 
    
    elif get_by_id(id).sender_id != get_user_or_raise_401(x_token).id:
        return JSONResponse(status_code=401, content='You are allowed to delete only your sent messages.')
    
    delete_message(id)

    return {'Message deleted.'}
