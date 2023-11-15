from fastapi import APIRouter
from fastapi.responses import JSONResponse
from datetime import datetime
from services import date_service


date_router = APIRouter(prefix='/date', tags=['Date'])


@date_router.get('/', description='Check current date.')
def check_current_date():
    # Today is the last date set in the database
    info = date_service.current_date()
    return {"Today is": info}


@date_router.post('/{date}', description='Set specific date in the future in format "yyyy-mm-dd" (2023-03-15).')
def set_specific_date(date: str):
    # check format is correct
    try:
        new_date = datetime.strptime(date, "%Y-%m-%d")
        new_date = datetime.date(new_date)
    except ValueError:
        return JSONResponse(status_code=400, content="The date must be in format 'yyyy-mm-dd' (2023-03-15)")

    # check if date is not in past
    date_service.date_is_in_future(date)

    # set the new date
    return date_service.add_date(date)


# TODO: add days to date
# @date_router.post('/{days}', description='Specify the number of days in the future.')
# def number_of_days(days: int):
#     if days <= 0:
#         return JSONResponse(status_code=400, content="The number must be positive.")
#
#     today = current_date()
#     new_date = today + timedelta(days= days)
#     return add_date(new_date)



