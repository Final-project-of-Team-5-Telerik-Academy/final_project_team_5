from fastapi import APIRouter, Query, Header, Form
from fastapi.responses import JSONResponse
from services import match_service, team_service
from authentication.authenticator import get_user_or_raise_401, get_user_from_token
from services import shared_service
from my_models.model_user import User
from datetime import datetime, date
from my_models.model_player import Player
from pydantic import constr, conint
from services import player_service


matches_router = APIRouter(prefix='/matches', tags=['Matches'])



" 1. VIEW MATCHES"
@matches_router.get('/', description='You can view all matches')
def view_all_matches(sort: str = Query(description='sort by date: asc / desc', default='asc'),
                    status: str = Query(description='filter by: all / played / upcoming', default='all')):

    result = match_service.get_all_matches(status, sort)
    return result



" 2. VIEW MATCH BY ID"
@matches_router.get('/{id}', description='You can view all matches')
def view_match_by_id(id: int):
    result = match_service.get_match_by_id(id)
    if not result:
        return f'There is no match with id {id}.'
    return result





" 3. CREATE MATCH"
@matches_router.post('/create/one_on_one/{match_id}', description='You can create new match')
def create_match(token: str = Header(),
                 match_format: str = Form('time limit', description="Select an option",
                                    enum=['time limit', 'score limit']),
                 game_type: str = Form('one on one', description="Select an option",
                                    enum=['one on one', 'team game']),
                 participant_1: str = Query(),
                 participant_2: str = Query(),
                 date: str = Query(description='write date in format yyyy-mm-dd'),
                 tournament_name: str = Query(default='not part of a tournament')):

# check if authenticated and role
    user = get_user_or_raise_401(token)
    date = datetime.strptime(date, "%Y-%m-%d").date()
    if not (User.is_director(user) or User.is_admin(user)):
        return JSONResponse(status_code=403, content='Only Admin and Director can create a match')
    if participant_1 == participant_2:
        return JSONResponse(status_code=400, content='Choose different players')

    if game_type == 'one on one':
        participant_1 = match_service.check_create_player(participant_1)
        participant_2 = match_service.check_create_player(participant_2)

    elif game_type == 'team game':
        participant_1 = team_service.get_team_by_name(participant_1)
        participant_2 = team_service.get_team_by_name(participant_2)

    match = match_service.create_match(match_format, game_type, participant_1,
            participant_2, user.full_name, date, tournament_name)
    return match









"ENTER MATCH WINNER"
@matches_router.put('/enter_winner/{id}')
def enter_match_winner(id: int, token: str, winner: str):
# check if authenticated and role
    user = get_user_or_raise_401(token)
    if not (User.is_director(user) or User.is_admin(user)):
        return JSONResponse(status_code=403, content='Only Admin and Director can create a match')

    match = match_service.get_match_by_id(id)
    if  match is None:
        return JSONResponse(status_code=404, content='There is no match with that id')
    if match.participant_1 is not winner or match.participant_2 is not winner:
        return JSONResponse(status_code=400, content=f"{winner} doesn't play in this match")
    winner = match_service.set_winner(winner, match)

# TODO team match
""" 
"CREATE MATCH TEAM GAME"    
@matches_router.post('/create/team_game', description='You can create new match')
def create_match_one_on_one(token: str = Header(),
                 match_format: str = Form(..., description="Select an option",
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
    match = match_service.create_match(match_format, 'one on one', participant_1, participant_2, date)
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


