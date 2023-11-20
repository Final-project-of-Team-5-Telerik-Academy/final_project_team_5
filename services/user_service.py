from data.database import read_query, insert_query, update_query
from my_models.model_user import Role, User
# from my_models.model_tournament import Tournament # Да се откоментира, когато се напише класа Tournament!
from authentication.authenticator import find_by_email
from my_models.model_admin_requests import AdminRequests


_SEPARATOR = ';'


def _hash_password(password: str):
    ''' Used to hash a password of a user before saving it in the database.'''
    from hashlib import sha256
    return sha256(password.encode('utf-8')).hexdigest()


def try_login(email: str, password: str) -> User | None:
    ''' Used to hash the login password and compare it with the existing password of the user in the database.'''

    user = find_by_email(email)

    password = _hash_password(password)
    return user if user and user.password == password else None


def create(full_name: str, email: str, password: str, gender: str) -> User | None:
    ''' Automatically creates id for the user and inserts all the user's data in the database in the row of the same id.
    
        Args:
        - full_name: str
        - email: str
        - hashed password: str
        - gender: str

        Returns:
            - Class User
    '''
    
    password = _hash_password(password)
    
    role = Role.SPECTATOR
    players_id = None

    generated_id = insert_query(
        'INSERT INTO users(full_name, email, password, gender, role, players_id) VALUES (?,?,?,?,?,?)',
        (full_name, email, password, gender, role, players_id)
    )

    return User(id=generated_id, full_name=full_name, email=email, password='******', gender=gender, role=role, players_id=players_id)


def delete_account(id: int):
    ''' Used for deleting user's own account from the database.'''

    insert_query('''DELETE FROM users WHERE id = ?''',
                 (id,))


def find_all_user_requests(id: int) -> AdminRequests | None:
    ''' Search in the database and creates a list of all user's requests.
    
    Returns:
        - a list of all user's requests (id, type_of_request, players_id, users_id, status)
    '''

    data = read_query('SELECT id, type_of_request, players_id, users_id, status FROM admin_requests WHERE users_id = ?',
        (id,))

    return (AdminRequests.from_query_result(*row) for row in data)
    

def find_request_by_id_and_users_id(id: int, users_id: int) -> AdminRequests | None:
    ''' Search in the database and returns user's requests by ID.
    
    Returns:
        - a request of user (id, type_of_request, players_id, users_id, status)
    '''

    data = read_query('SELECT id, type_of_request, players_id, users_id, status FROM admin_requests WHERE id = ? and users_id = ?',
        (id, users_id))

    return next((AdminRequests.from_query_result(*row) for row in data), None)


# !!! Да се откоментира, когато се напише класа Tournament! Проверява дали турнамента е създаден от същия директор. Може да се използва за edit или delete на турнамент. !!!
# def owns_tournament(user: User, tournament: Tournament) -> bool:
#     ''' Used to compare the tournament.user_id with the user's token id.'''
    
#     return tournament.user_id == user.id


def send_connection_request(type_of_request:str, players_id:int, users_id:int) -> AdminRequests | None:
    ''' Creates an ID and saves the connection request in the database.
    
    Args:
        - type_of_request: str
        - players_id: int
        - users_id: int

    Returns:
        - created request for connection
    '''

    status = 'pending'

    generated_id = insert_query(
        'INSERT INTO admin_requests(type_of_request, players_id, users_id, status) VALUES (?,?,?,?)',
        (type_of_request, players_id, users_id, status)
    )

    return AdminRequests(id=generated_id, type_of_request=type_of_request, players_id=players_id, users_id=users_id, status=status)


def send_promotion_request(type_of_request:str, users_id:int) -> AdminRequests | None:
    ''' Creates an ID and saves the promotion request in the database.
    
    Args:
        - type_of_request: str
        - users_id: int

    Returns:
        - created request for promotion
    '''

    status = 'pending'
    generated_id = insert_query(
        'INSERT INTO admin_requests(type_of_request, users_id, status) VALUES (?,?,?)',
        (type_of_request, users_id, status)
    )
    # ДА СЕ ИЗПОЛЗВА КОГАТО АДМИН УДОБРЯВА АДМИН REQUEST
    # is_active = 1
    # players_id = User.players_id #TODO
    # update_query('''UPDATE players SET is_active = ? WHERE id = ?''',
    #             (is_active, players_id))
    return AdminRequests(id=generated_id, type_of_request=type_of_request, users_id=users_id, status=status)


def get_user_full_name_by_id(user_id: str):
    user_name = read_query('SELECT full_name FROM users WHERE id = ?', (user_id,))
    return user_name[0][0]

