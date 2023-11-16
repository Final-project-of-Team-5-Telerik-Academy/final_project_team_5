from fastapi import APIRouter, Query, Header
from fastapi.responses import JSONResponse
from services import  date_service, tournament_service
from authentication.authenticator import get_user_or_raise_401, get_user_from_token




tournaments_router = APIRouter(prefix='/tournaments', tags=['Tournaments'])


@tournaments_router.post('/create')
def create_tournament(token: str = Header(),
                      title: str = Query(min_length=5),
                      format: str = Query(description='time limit or score limit'),
                      date: str = Query(description='write date in format yyyy-mm-dd'),
                      prize: int = Query(gt=100)):

# check if authenticated
    get_user_or_raise_401(token)

# check role
    creator = get_user_from_token(token)
    if creator.role not in ['admin', 'director']:
        return JSONResponse(status_code=403, content='Only Admin and Director can create a tournament')

# check if the date is in the future
    date_service.date_is_in_future(date)

# creating new tournament
    tournament_service.create_tournament(title, format, date, prize, creator)


