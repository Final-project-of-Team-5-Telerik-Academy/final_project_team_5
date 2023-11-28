from fastapi import APIRouter, Query, Header, Form
from fastapi.responses import JSONResponse
from services import match_service, team_service, shared_service
from authentication.authenticator import get_user_or_raise_401
from my_models.model_user import User
from my_models.model_match import sports_list
from datetime import datetime


matches_router = APIRouter(prefix='/matches', tags=['Matches'])


" 1. VIEW MATCHES"
@matches_router.post('/', description='You can view all matches')
def view_all_matches(sort: str = Form('asc', description='sort by date',
                                      enum=['asc', 'desc']),
                    status: str = Form('all', description='filter',
                                       enum=[ 'all', 'played', 'upcoming'])):

    result = match_service.get_all_matches(status, sort)
    return result



" 2. VIEW MATCH BY ID"
@matches_router.get('/{id}', description='You can view all matches')
def view_match_by_id(id: int):
    result = match_service.get_match_by_id(id)
    if not result:
        return JSONResponse(status_code=404, content=f'There is no match with id {id}.')
    return result



" 3. CREATE MATCH"
@matches_router.post('/create/{match}', description='You can create new match')
def create_match(token: str,
                 game_type: str = Form('one on one', description="Select an option",
                                    enum=['one on one', 'team game']),
                 sport: str = Form(..., description="Select a kind of sport",
                                   enum=sports_list),
                 match_format: str = Form('time limit', description="Select an option",
                                          enum=['time limit', 'score limit']),
                 participant_1: str = Query(),
                 participant_2: str = Query(),
                 date: str = Query(description='write date in format yyyy-mm-dd'),
                 tournament_name: str = Query(default='not part of a tournament')):

# check if authenticated and role
    user = get_user_or_raise_401(token)
    if not (User.is_director(user) or User.is_admin(user)):
        return JSONResponse(status_code=403, content='Only Admin and Director can create a match')

    shared_service.check_date_format(date)
    date = datetime.strptime(date, "%Y-%m-%d").date()

    if participant_1 == participant_2:
        return JSONResponse(status_code=400, content='Choose different players')

    output = []
    if game_type == 'one on one':
        p1 = match_service.check_create_player(participant_1)
        p2 = match_service.check_create_player(participant_2)
        output.append(p1) if p1 else None
        output.append(p2) if p1 else None

    elif game_type == 'team game':      # TODO: check team exists
        participant_1 = team_service.get_team_by_name(participant_1)
        participant_1 = participant_1.team_name

        participant_2 = team_service.get_team_by_name(participant_2)
        participant_2 = participant_2.team_name

    match = match_service.create_match(match_format, game_type, sport, participant_1,
            participant_2, user.full_name, date, tournament_name)
    output.append(match)

    return [el for el in output]



" 4. ENTER MATCH WINNER"
@matches_router.put('/')
def enter_match_winner(token: str, match_id: int, winner: str,
                       p1_score: float = Query(description='Enter participant 1 score'),
                       p2_score: float = Query(description='Enter participant 2 score')):

    user = get_user_or_raise_401(token)
    if not (User.is_director(user) or User.is_admin(user)):
        return JSONResponse(status_code=403, content='Only Admin and Director can create a match')

    match = match_service.get_match_by_id(match_id)
    if  match is None:
        return JSONResponse(status_code=404, content='There is no match with that id')

    if match.winner != 'not played':
        return JSONResponse(status_code=400,
            content=f'The winner of match {match.id} is already set to {match.winner}.')

    if match.participant_1 == winner and match.participant_2 == winner:
        return JSONResponse(status_code=400, content=f"{winner} doesn't play in this match")

    winner = match_service.set_winner(winner, match, p1_score, p2_score,)
    return winner




" 5. DELETE A MATCH"
@matches_router.delete('/{id}')
def delete_match(id: int, token: str):
    user = get_user_or_raise_401(token)
    if not (User.is_director(user) or User.is_admin(user)):
        return JSONResponse(status_code=403, content='Only Admin and Director can create a match')
    match = match_service.get_match_by_id(id)
    if not match:
        return JSONResponse(status_code=404, content=f'There is no match with id {id}.')

    result = match_service.delete_match(id)
    return result







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


