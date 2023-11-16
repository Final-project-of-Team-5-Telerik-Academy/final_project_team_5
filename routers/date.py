from fastapi import APIRouter
from fastapi.responses import JSONResponse
from datetime import datetime, timedelta
from services import date_service, match_service
from authentication.authenticator import get_user_or_raise_401
import re

date_router = APIRouter(prefix='/dates', tags=['Date'])


@date_router.get('/', description='Check current date.')
def check_current_date(token):
    get_user_or_raise_401(token)

# Today is the last date set in the database
    info = date_service.current_date()
    return {"Today is": info}



@date_router.post('/{date}', description='Set specific date in the future in format "yyyy-mm-dd" (2023-3-15).')
def set_specific_date(date: str, token):
# check if authenticated
    get_user_or_raise_401(token)

# check format is correct
    pattern = re.compile(r'^\d{4}-\d{2}-\d{2}$')
    if not pattern.match(date):
        return JSONResponse(status_code=400, content="The date must be in format 'yyyy-mm-dd' (2023-3-15)")

# check if date is not in past
    format_date = datetime.strptime(date, "%Y-%m-%d").date()
    date_service.date_is_in_future(format_date)

# play upcoming matches before this date
    match_service.play_matches(format_date)

# remove injuries
#     player_service.remove_injuries()

# set the new date
    return date_service.add_date(format_date)



@date_router.post('/{days}', description='Specify the number of days in the future.')
def number_of_days(days: int):
    if days <= 0:
        return JSONResponse(status_code=400, content="The number must be positive.")

    today = date_service.current_date()
    new_date = today + timedelta(days= days)
    result = date_service.add_date(new_date)
    return result


