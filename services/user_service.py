from data.database import read_query, insert_query, update_query
from my_models.model_user import Role, User
# from my_models.model_tournament import Tournament # Да се откоментира, когато се напише класа Tournament!
from authentication.authenticator import find_by_email


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
    

# Да се откоментира, когато се напише класа Tournament! Проверява дали турнамента е създаден от същия директор. Може да се използва за edit или delete на турнамент.
# def owns_tournament(user: User, tournament: Tournament) -> bool:
#     ''' Used to compare the tournament.user_id with the user's token id.'''
    
#     return tournament.user_id == user.id


