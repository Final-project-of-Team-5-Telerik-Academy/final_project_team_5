from data.database import read_query,insert_query
from my_models.model_user import User 
from datetime import datetime

_SEPARATOR = ';'

def read_users():

    data = read_query('SELECT * FROM new_user')

    return data

def find_by_username(nickname: str) -> User | None:
    data = read_query(
        'SELECT * FROM new_user WHERE nickname = ?',
        (nickname,))

    return next((User.from_query_result(*row) for row in data), None)

def find_user_by_id(id: int) -> User | None:
    data = read_query(
        'SELECT * FROM new_user WHERE id_of_user = ?',
        (id,))

    return data[0][2]


def check_username_exist(nickname:str) -> bool:

    data = read_query(
        'SELECT nickname FROM new_user WHERE nickname = ?',
        (nickname,)
    )

    return bool(data)

def check_email_exist(email:str) -> bool:

    data = read_query(
        'SELECT email FROM new_user WHERE email = ?',
        (email,)
    )

    return bool(data)

def try_login(username: str, password: str) -> User | None:
    user = find_by_username(username)

    return user if user and user.password == password else None

def create_token(user: User) -> str:
    return f'{user.id}{_SEPARATOR}{user.nickname}'


def is_authenticated(token: str) -> bool:
    return any(read_query(
        'SELECT 1 FROM new_user WHERE id_of_user = ? and nickname = ?',
        token.split(_SEPARATOR)))


def from_token(token: str) -> User | None:
    _, nickname = token.split(_SEPARATOR)

    return find_by_username(nickname)

def get_username_by_token(token: str):
    _, nickname = token.split(_SEPARATOR)
    return nickname

def create_user(email: str, nickname: str, password: str, dateOfBirth, gender: str) -> User | None:

        generated_id = insert_query(
            'INSERT INTO new_user(email, nickname, password, date_of_birth, gender) VALUES (?,?,?,?,?)',
            (email, nickname, password, dateOfBirth, gender))

        return User(id=generated_id, email=email,nickname=nickname, password=password, date=dateOfBirth, gender=gender)

def find_user_by_token(token: str):

    splitted_token = token.split(';')

    return splitted_token[0]

def find_username_by_token(token: str):

    splitted_token = token.split(';')

    return splitted_token[1]

def find_username_by_id(username: str):
    user = read_query('SELECT id_of_user FROM new_user WHERE nickname = ?', (username,))
    
    if user:
        return user[0][0]
    
def get_id_by_token(token: str):
    user_id, _ = token.split(_SEPARATOR)
    return int(user_id)

def from_token_2(token: str) -> User | None:
    user_id = get_id_by_token(token)
    return find_id_by_token(user_id)

def find_id_by_token(token: str) -> int | None:
    data = read_query(
        'SELECT id_of_user FROM new_user WHERE token = ?',
        (token,))
    
    if data:
        return data[0][0]
    return None


def get_username_by_user_id(user_id: int):
    username = read_query('SELECT nickname FROM new_user WHERE id_of_user = ?',
                          (user_id,))
    return username[0][0]

def find_nickname_by_new_id(id: int) -> User | None:
    data = read_query(
        'SELECT nickname FROM new_user WHERE id_of_user = ?',
        (id,))
    return data[0][0]