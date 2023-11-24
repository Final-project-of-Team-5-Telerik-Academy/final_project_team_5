from fastapi import APIRouter, Query, Header, Form
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



"VIEW MATCHES"
@matches_router.get('/', description='You can view all matches')
def view_all_matches(sort: str = Query(description='sort by date: asc / desc', default='asc'),
                    status: str = Query(description='filter by: all / played / upcoming', default='all')):

    result = match_service.get_all_matches(status, sort)
    return result



@matches_router.get('/{id}', description='You can view all matches')
def view_match_by_id(id: int):
    result = match_service.get_match_by_id(id)
    if not result:
        return f'There is no match with id {id}.'
    return result



"CREATE MATCH ONE ON ONE"
@matches_router.post('/create/one_on_one/{match_id}', description='You can create new match')
def create_match_one_on_one(token: str = Header(),
                 format: str = Form(..., description="Select an option",
                                    example='time limit', enum=['time limit', 'score limit']),
                 participant_1: str = Query(),
                 participant_2: str = Query(),
                 date: str = Query(description='write date in format yyyy-mm-dd'),
                 tournament_name: str = Query(default='not part of a tournament')):

# check if authenticated and role
    user = get_user_or_raise_401(token)
    if not (User.is_director(user) or User.is_admin(user)):
        return JSONResponse(status_code=403, content='Only Admin and Director can create a match')

# check if the date is in the future
    if not date_service.date_is_in_future(date):
        today = date_service.current_date()
        return JSONResponse(status_code=400, content=f"Today is {today}. You must choose date in th future")

    date = datetime.strptime(date, "%Y-%m-%d").date()
    output = []
# get player 1
    existing_player = player_service.get_player_by_full_name(participant_1)
    if existing_player is None:
        participant_1 = player_service.create_player(participant_1, 'add country', 'add sport club')
        participant_1 = participant_1.full_name
        output.append({"Warning": f'''Participant 1 dose not exist in the system. 
                    We've created profile for him, but it is uncompleted. You must finish it!'''})
    else:
        if not existing_player.is_active:
            return f'{existing_player} is not activ player.'
        participant_1 = existing_player.full_name

# get player 2
    existing_player = player_service.get_player_by_full_name(participant_2)
    if existing_player is None:
        participant_2 = player_service.create_player(participant_2, 'add country', 'add sport club')
        participant_2 = participant_2.full_name
        output.append({"Warning": f'''Participant 1 dose not exist in the system. 
                    We've created profile for him, but it is uncompleted. You must finish it!'''})
    else:
        if not existing_player.is_active:
            return f'{existing_player} is not activ player.'
        participant_2 = existing_player.full_name

    if participant_1 == participant_2:
        return JSONResponse(status_code=400, content='Choose different players')

    # create match
    match = match_service.create_match(
        format, 'one on one', participant_1, participant_2, date, tournament_name)
    output.append(match)
    return match


# TODO team match
""" 
"CREATE MATCH TEAM GAME"    
@matches_router.post('/create/team_game', description='You can create new match')
def create_match_one_on_one(token: str = Header(),
                 format: str = Form(..., description="Select an option",
                                    example='time limit', enum=['time limit', 'score limit']),
                 participant_1: str = Query(),
                 participant_2: str = Query(),
                 date: str = Query(description='write date in format yyyy-mm-dd')):

# check if authenticated and role
    user = get_user_or_raise_401(token)
    if not (User.is_director(user) or User.is_admin(user)):
        return JSONResponse(status_code=403, content='Only Admin and Director can create a match')

# check if the date is in the future
    if not date_service.date_is_in_future(date):
        today = date_service.current_date()
        return JSONResponse(status_code=400, content=f"Today is {today}. You must choose date in th future")

    date = datetime.strptime(date, "%Y-%m-%d").date()
    output = []
# get player 1
    existing_player = player_service.get_player_by_full_name(participant_1)
    if existing_player is None:
        participant_1 = player_service.create_player(participant_1, 'add country', 'add sport club')
        output.append({"Warning": f'''Participant 1 dose not exist in the system. 
                    We've created profile for him, but it is uncompleted. You must finish it!'''})
    else:
        if not existing_player.is_active:
            return f'{existing_player} is not activ player.'
        participant_1 = existing_player.full_name

# get player 2
    existing_player = player_service.get_player_by_full_name(participant_2)
    if existing_player is None:
        participant_2 = player_service.create_player(participant_2, 'add country', 'add sport club')
        output.append({"Warning": f'''Participant 1 dose not exist in the system. 
                    We've created profile for him, but it is uncompleted. You must finish it!'''})
    else:
        if not existing_player.is_active:
            return f'{existing_player} is not activ player.'
        participant_2 = existing_player.full_name

    # create match
    match = match_service.create_match(format, 'one on one', participant_1, participant_2, date)
    output.append(match)
    return match
"""







"UPDATE MATCH DATE" # TODO
# @matches_router.put('/update/{date}')
# def update_match_date(token, current_title: str, new_date: str):
#     current_table = 'matches'
#     column = 'date'
#     format_date = datetime.strptime(new_date, "%Y-%m-%d").date()
#
# # check if authenticated
#     user = get_user_or_raise_401(token)
#
# # check admin or creator
#     creator_name = shared_service.get_creator_full_name(current_table, current_title)
#     if not (user.full_name == creator_name or User.is_admin(user)):
#         return JSONResponse(status_code=403, content='Only Admin and creator can assign players to match')
#
# # check if the date is in the future
#     if not date_service.date_is_in_future(format_date):
#         today = date_service.current_date()
#         return JSONResponse(status_code=400, content=f"Today is {today}. You must choose date in th future")
#
# # update match date
#     match_service.update_match_details(current_title, column, format_date)
#     return {f'Match "{current_title}" moved to a date of "{format_date}"'}



# @matches_router.put('/update/{format}')
# def update_match_date(token, current_title: str, new_format: str):
#     current_table = 'matches'
#     column = 'date'
#
# # check if authenticated
#     user = get_user_or_raise_401(token)
#
# # check admin or creator
#     creator_name = shared_service.get_creator_full_name(current_table, current_title)
#     if not (user.full_name == creator_name or User.is_admin(user)):
#         return JSONResponse(status_code=403, content='Only Admin and creator can assign players to match')
#
# # check if the date is in the future
#     if not date_service.date_is_in_future(format_date):
#         today = date_service.current_date()
#         return JSONResponse(status_code=400, content=f"Today is {today}. You must choose date in th future")
#
# # update match date
#     match_service.update_match_details(current_title, column, format_date)
#     return {f'Match "{current_title}" moved to a date of "{format_date}"'}
#

#                          match_format: constr(pattern='^time limit|score limit$'),
#                          prize: conint(gt=-1)):


