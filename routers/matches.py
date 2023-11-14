from fastapi import APIRouter, Query, Header
from fastapi.responses import JSONResponse
from services import match_service, player_service
from authentication.authenticator import get_user_or_raise_401, get_user_from_token
from typing import Annotated
from my_models import model_user



matches_router = APIRouter(prefix='/matches', tags=['Matches'])

@matches_router.post('/', description='You can create new match')
def create_match(token: str = Header(),
                 date: str = Query(description='write date in format yyyy-mm-dd'),
                 player_1: str = Query(min_length=5),
                 player_2: str = Query(min_length=5),
                 match_format: str = Query(description='time limit or score limit'),
                 prize: int = Query(gt=100),
                 tournament_name: Annotated[str | None, Query(min_length=5)] = None):

    # check if authenticated
    get_user_or_raise_401(token)

    # check role
    user = get_user_from_token(token)
    if not user.role == "director" or not user.role == 'admin':
        return JSONResponse(status_code=403, content='Only Admin and Director can create a match')

    # check if the date is in the past
    # today = "?" # TODO: да изведа в отделна функция и папка
    # if date < today:
    #     return JSONResponse(content=f'Today is {today}. You can not create a match in the past.')

    # check if the players are exist in the system
    messages = []
    if not player_service.player_exists(player_1):
        player_service.create_uncompleted_player(player_1)
        message = {"Warning": f'''Player '{player_1}' dose not exist in the system.
                            We've created profile for him, but it is uncompleted.
                            You must finish the player's profile!'''}
        messages.append(message)

    if not player_service.player_exists(player_2):
        player_service.create_uncompleted_player(player_2)
        message = {"Warning": f'''Player '{player_1}' dose not exist in the system.
                            We've created profile for him, but it is uncompleted.
                            You must finish the player's profile!'''}
        messages.append(message)

    #check if match format is correct
    if tournament_name:
        allowed_formats = ['time limit', 'score limit']
    else:
        allowed_formats = ['time limit']

    available_formats = ', '.join(allowed_formats)
    if match_format not in allowed_formats:
        return JSONResponse(content=f'Available formats for this match is: {available_formats}.')

    # creating new match
    title = f'{player_1} vs {player_2}'
    creator = token
    match = match_service.create_match(date, title, player_1, player_2, match_format, prize, creator, tournament_name, )
    return match




@matches_router.get('/', description='You can view all matches')
def view_all_matches(title: str = Query(None),
                     sort: str = Query(default='ascending',
                     description='You can choose to sort')):
    if title:
        return match_service.get_match_by_title(title)
    elif sort:
        return match_service.get_sorted_matches(sort)
    else:
        return match_service.get_all_matches()


# @matches_router.put('/{title}')
# def update_match(x_token: str = Header(..., description="User's authentication token"),
#                 title: str = Query(),
#                 date: str = Query(),
#                 match_format: str = Query(),
#                 prize: int = Query(gt=100),
#                 tournament_name: Annotated[str | None, Query(min_length=5)] = None):
#
#     if not x_token == "director":
#         return JSONResponse(content='Only admin and director can update matches')






























