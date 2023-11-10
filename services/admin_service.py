from data.database import read_query, insert_query, update_query
from my_models.model_user import User


_SEPARATOR = ';'


def find_all_users() -> User | None:
    ''' Search in the database and creates a list of all users. Only admins can view a list of all users.
     
    Returns:
        - a list of all users(id, full_name, email, gender, role, players_id)
    '''

    data = read_query('SELECT id, full_name, email, password, role, players_id FROM users')

    result = (User.from_query_result_no_password(*row) for row in data)

    return result


def find_user_by_id(id: int) -> User | None:
    ''' Search through users.id the whole information about the account in the data. Only admins can search for them.
     
    Args:
        - id: int 
        
    Returns:
        - all the necessary information about the user (id, full_name, email, gender, role, players_id)
    '''

    data = read_query(
        'SELECT id, full_name, email, password, gender, role, players_id FROM users WHERE id = ?',
        (id,))

    return next((User.from_query_result_no_password(*row) for row in data), None)


def edit_user(old_user: User, new_role: str):
    ''' Used for editing by an admin a role of a user in the database.'''
    
    edited_user = User(
        id=old_user.id,
        full_name=old_user.full_name,
        email=old_user.email,
        password=old_user.password,
        gender=old_user.gender,
        role=new_role,
        players_id=old_user.players_id
    )

    update_query('''UPDATE users SET role = ? WHERE id = ?''',
                (edited_user.role, edited_user.id))

    return {"User's role is updated."}


def delete_user(id: int):
    ''' Used for deleting the user from the database.'''

    insert_query('''DELETE FROM users WHERE id = ?''',
                 (id,))
    
