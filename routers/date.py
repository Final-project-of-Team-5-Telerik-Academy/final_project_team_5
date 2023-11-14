from fastapi import APIRouter
from fastapi.responses import JSONResponse
from data.database import read_query, insert_query
from datetime import datetime, timedelta



date_router = APIRouter(prefix='/date', tags=['Date'])


@date_router.get('/', description='Check current date.')
def check_current_date():
    # Today is the last date set in the database
    info = current_date()
    return {"Today is": info}



@date_router.post('/{date}', description='Set specific date in the future in format "yyyy-mm-dd" (2023-3-15).')
def set_specific_date(date: str):
    # check format is correct
    try:
        new_date = datetime.strptime(date, "%Y-%m-%d")
        new_date = datetime.date(new_date)
    except ValueError:
        return JSONResponse(status_code=400, content="The date must be in format 'yyyy-mm-dd' (2023-3-15)")

    # check date if date is not in past
    today = current_date()
    if today >= new_date:
        return JSONResponse(status_code=400, content="The date must be in teh future")

    # set the new date
    return add_date(date)


# TODO: add days to date
# @date_router.post('/{days}', description='Specify the number of days in the future.')
# def number_of_days(days: int):
#     if days <= 0:
#         return JSONResponse(status_code=400, content="The number must be positive.")
#
#     today = current_date()
#     new_date = today + timedelta(days= days)
#     return add_date(new_date)



def current_date():
    # Today is the last date set in the database
    info_from_db = read_query('SELECT date FROM dates ORDER BY id desc LIMIT 1')
    today_is = info_from_db[0][0]
    return today_is



def add_date(date: str):
    insert_query('INSERT INTO dates(date) VALUE (?)', (date,))
    return {f'The current date is set to {date}'}