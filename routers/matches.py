from fastapi import APIRouter, Query, Header
from fastapi.responses import JSONResponse
from services import match_service, date_service
from authentication.authenticator import get_user_or_raise_401, get_user_from_token
from services import shared_service
from my_models.model_user import User
from datetime import datetime, date
from my_models.model_player import Player
from pydantic import constr, conint
from services import player_service


matches_router = APIRouter(prefix='/matches', tags=['Matches'])

@matches_router.post('/', description='You can create new match')
def create_match(token: str = Header(),
                 date: str = Query(description='write date in format yyyy-mm-dd'),
                 title: str = Query(),
                 match_format: str = Query(description='time limit or score limit'),
                 prize: int = 0):

# check if authenticated
    user = get_user_or_raise_401(token)

# check role
    if not (User.is_director(user) or User.is_admin(user)):
        return JSONResponse(status_code=403, content='Only Admin and Director can create a match')

# check if the date is in the future
    if not date_service.date_is_in_future(date):
        today = date_service.current_date()
        return JSONResponse(status_code=400, content=f"Today is {today}. You must choose date in th future")

# create match
    date = datetime.strptime(date, "%Y-%m-%d").date()
    creator = user.full_name
    match = match_service.create_match(title = title, date = date, match_format = match_format, prize = prize, creator=creator)
    return match



@matches_router.put('/assign')
def assign_player_to_match(token: str, match_title: str, player_name: str, team: int):
    table = 'matches'

# check if authenticated
    user = get_user_or_raise_401(token)

# check admin or creator
    creator_name = match_service.get_creator_full_name(table, match_title)
    if not (user.full_name == creator_name or User.is_admin(user)):
        return JSONResponse(status_code=403, content='Only Admin and creator can assign players to match')

# check if match exists
    match = match_service.get_match_by_title(match_title)
    if not match:
        return JSONResponse(status_code=404, content=f'Match "{match_title}" does not exists.')

# get or create player
    country = 'add country'
    sports_club = 'add sport club'
    if not shared_service.full_name_exists(player_name, table):
        player_to_assign = player_service.create_player(player_name, country, sports_club)
        return {"Warning": f'''Player '{player_to_assign}' dose not exist in the system.
                            We've created profile for him, but it is uncompleted. You must finish the player's profile!'''}
    else:
# TODO: get object player from DB
        player_to_assign = Player()

# check if player is injured
        if player_to_assign.is_injured:
            return f'{player_to_assign} is injured at the moment and cannot participate in this match'

# assign player to match
    match_service.assign_player_to_match(match, player_to_assign, team)
    return {"message": f"{player_to_assign.full_name} assigned to {match.title}"}



@matches_router.put('/change/{player}')
def change_player_team_in_match(token: str, match_title: str, player_name: str, desired_team: int):
    current_table = 'matches'

# check if authenticated
    user = get_user_or_raise_401(token)

# check admin or creator
    creator_name = match_service.get_creator_full_name(current_table, match_title)
    if not (user.full_name == creator_name or User.is_admin(user)):
        return JSONResponse(status_code=403, content='Only Admin and creator can assign players to match')

# check if match exists
    match = match_service.get_match_by_title(match_title)
    if not match:
        return JSONResponse(status_code=404, content=f'Match "{match_title}" does not exists.')

# check if this player is assigned to this match
    assigned_player = Player()
    if not shared_service.players_id_exists(assigned_player.id, current_table):
        return JSONResponse(status_code=404, content=f'{player_name} is not assigned to {match_title}.')

# change player team in match
    match_service.change_player_team_in_match(match_title, player_name, desired_team)
    return {f'{player_name} now is in team {desired_team} for match {match_title}'}



@matches_router.get('/{title}', description='You can view all matches')
def view_match_by_title(title: str):
    result = match_service.get_match_by_title(title)
    return result



@matches_router.get('/played', description='You can view all matches')
def view_played_matches(sort: str = Query(default='ascending', description='You can choose to sort')):
    if sort:
        return match_service.get_sorted_matches(sort, status=True)
    else:
        return match_service.get_all_matches(status=True)



@matches_router.get('/upcoming')
def view_upcoming_matches(sort: str = Query(default='ascending', description='You can choose to sort')):
    if sort:
        return match_service.get_sorted_matches(sort, status=False)
    else:
        return match_service.get_all_matches(status=False)



@matches_router.put('/update/{title}')
def update_match_title(token, current_title: str, new_title: str):
    current_table = 'matches'
    column = 'title'

# check if authenticated
    user = get_user_or_raise_401(token)

# check admin or creator
    creator_name = match_service.get_creator_full_name(current_table, current_title)
    if not (user.full_name == creator_name or User.is_admin(user)):
        return JSONResponse(status_code=403, content='Only Admin and creator can assign players to match')

# update match title
    match_service.update_match_details(current_title, column, new_title)
    return {f'Match "{current_title}" was renamed to "{new_title}"'}



@matches_router.put('/update/{date}')
def update_match_date(token, current_title: str, new_date: str):
    current_table = 'matches'
    column = 'date'
    format_date = datetime.strptime(new_date, "%Y-%m-%d").date()

# check if authenticated
    user = get_user_or_raise_401(token)

# check admin or creator
    creator_name = match_service.get_creator_full_name(current_table, current_title)
    if not (user.full_name == creator_name or User.is_admin(user)):
        return JSONResponse(status_code=403, content='Only Admin and creator can assign players to match')

# check if the date is in the future
    if not date_service.date_is_in_future(format_date):
        today = date_service.current_date()
        return JSONResponse(status_code=400, content=f"Today is {today}. You must choose date in th future")

# update match date
    match_service.update_match_details(current_title, column, format_date)
    return {f'Match "{current_title}" moved to a date of "{format_date}"'}



@matches_router.put('/update/{format}')
def update_match_date(token, current_title: str, new_form: str):
    current_table = 'matches'
    column = 'date'

# check if authenticated
    user = get_user_or_raise_401(token)

# check admin or creator
    creator_name = match_service.get_creator_full_name(current_table, current_title)
    if not (user.full_name == creator_name or User.is_admin(user)):
        return JSONResponse(status_code=403, content='Only Admin and creator can assign players to match')

# check if the date is in the future
    if not date_service.date_is_in_future(format_date):
        today = date_service.current_date()
        return JSONResponse(status_code=400, content=f"Today is {today}. You must choose date in th future")

# update match date
    match_service.update_match_details(current_title, column, format_date)
    return {f'Match "{current_title}" moved to a date of "{format_date}"'}


#                          match_format: constr(pattern='^time limit|score limit$'),
#                          prize: conint(gt=-1)):


