from data.database import read_query, insert_query
from fastapi.responses import JSONResponse


def current_date():
    # Today is the last date set in the database
    info_from_db = read_query('SELECT date FROM dates ORDER BY id desc LIMIT 1')
    today_is = info_from_db[0][0]
    return today_is


def add_date(date: str):
    insert_query('INSERT INTO dates(date) VALUE (?)', (date,))
    return {f'The current date is set to {date}.'}


def date_is_in_future(date):
    today = current_date()
    if today >= date:
        return JSONResponse(status_code=400, content="The date must be in teh future!")
    return True