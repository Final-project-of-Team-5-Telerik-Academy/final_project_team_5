from data.database import read_query, insert_query
from datetime import datetime
from fastapi.responses import JSONResponse


def current_date():
    # Today is the last date set in the database
    info_from_db = read_query('SELECT date FROM dates ORDER BY id desc LIMIT 1')
    today_is = info_from_db[0][0]
    return today_is



def add_date(date):
    insert_query('INSERT INTO dates(date) VALUE (?)', (date,))
    return {f'The current date is set to {date}'}



def date_is_in_future(new_date):
    today = current_date()
    date = datetime.strptime(new_date, "%Y-%m-%d").date()

    return True if date >= today else False



