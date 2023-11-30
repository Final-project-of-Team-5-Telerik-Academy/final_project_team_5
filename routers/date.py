from fastapi import APIRouter
from fastapi.responses import JSONResponse
from datetime import datetime, timedelta
from services import date_service, match_service
from authentication.authenticator import get_user_or_raise_401
import re

date_router = APIRouter(prefix='/dates', tags=['Date'])


"CHECK CURRENT DATE"
@date_router.get('/', description='Check current date.')
def check_current_date():
    info = date_service.current_date()
    return {"Today is": info}



"SET SPECIFIC DATE IN THE FUTURE"
@date_router.post('/date/{future_date}', description='Set specific date in the future in format "yyyy-m-d" (2023-3-15).')
def set_specific_date(new_date: str):
# check format is correct    alternative: ^(0?[1-9]|[12][0-9]|3[01])[\/\-](0?[1-9]|1[012])[\/\-]\d{4}$
    pattern = re.compile(r'^\d{4}[\/\-](0?[1-9]|1[012])[\/\-](0?[1-9]|[12][0-9]|3[01])$')
    if not pattern.match(new_date):
        return JSONResponse(status_code=400, content="The date must be in format 'yyyy-m-d' (2023-3-15)")

# check if date is not in past
    if not date_service.date_is_in_future(new_date):
        return JSONResponse(status_code=400, content=f'Today is {date_service.current_date()}, please set a date in the future')

# play upcoming matches before this date
    new_date = datetime.strptime(new_date, "%Y-%m-%d").date()
    match_service.play_match(new_date)

# set the new date
    result = date_service.add_date(new_date)
    return result



"ADD NUMBER OF DAYS TO CURRENT DATE"
@date_router.patch('/days/{days}', description='Specify the number of days in the future.')
def add_number_of_days(days: int):
    if days <= 0:
        return JSONResponse(status_code=400, content="The number must be positive.")

# set the new date
    today = date_service.current_date()
    new_date = today + timedelta(days= days)
    result = date_service.add_date(new_date)
    return result


