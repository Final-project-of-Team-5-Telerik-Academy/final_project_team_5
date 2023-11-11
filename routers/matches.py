from fastapi import APIRouter, Query, Header
from fastapi.responses import JSONResponse
from services import match_service, player_service
from authentication.authenticator import get_user_or_raise_401
from typing import Annotated




matches_router = APIRouter(prefix='/matches', tags=['Matches'])

@matches_router.post('/', description='You can create new match')
def create_match(x_token: str = Header(),
                date: str = Query(),
                player_1: str = Query(min_length=5),
                player_2: str = Query(min_length=5),
                match_format: str = Query(),
                prize: int = Query(gt=100),
                tournament_name: Annotated[str | None, Query(min_length=5)] = None):

    # check real user
    get_user_or_raise_401(x_token)

    # check if the date is in the past
    today = "?" # TODO
    if date < today:
        return JSONResponse(content=f'Today is {today}. You can not create a match in the past.')

    # check if the players are exist in the system
    messages = []
    if not player_service.player_exists(player_1):
        player_service.create_uncompleted_player()
        message = {"Warning": f'''Player '{player_1}' dose not exist in the system.
                            We've created profile for him, but it is uncompleted.
                            You must finish the player's profile!'''}
        messages.append(message)

    if not player_service.player_exists(player_2):
        player_service.create_uncompleted_player()
        message = {"Warning": f'''Player '{player_1}' dose not exist in the system.
                            We've created profile for him, but it is uncompleted.
                            You must finish the player's profile!'''}
        messages.append(message)

    #check if match format is correct
    if tournament_name:
        allowed_formats = ['time_limit', 'score_limit']
    else:
        allowed_formats = ['time_limit']

    available_formats = ', '.join(allowed_formats)
    if match_format not in allowed_formats:
        return JSONResponse(content=f'Available formats for this match is: {available_formats}.')


    # creating new match
    title = f'{player_1} vs {player_2}'
    result = match_service.create_match(date, title, player_1, player_2, match_format, prize, tournament_name)


    # format = constr(pattern='^knockout|league$')



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





























