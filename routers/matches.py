from fastapi import APIRouter, Query, Header, Form
from fastapi.responses import JSONResponse
from services import match_service, team_service, shared_service, tournament_service, player_service
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


" 1.1. VIEW MATCHES BY TOURNAMENT"
@matches_router.get('/{title}/matches')
def view_matches_by_tournament(title: str):
    tournament = tournament_service.get_tournament_by_title(title)
    if tournament is None:
        return JSONResponse(status_code=404, content=f'Tournament with name {title} not found.')
    result = match_service.get_matches_by_tournament(title)
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
                 game_type: str = Form('one on one', enum=['one on one', 'team game']),
                 sport: str = Form(..., enum=sports_list),
                 match_format: str = Form('time limit', enum=['time limit', 'score limit']),
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
        output.append(match_service.check_create_player(participant_1))
        output.append(match_service.check_create_player(participant_2))

    elif game_type == 'team game':      # TODO: check team exists
        participant_1 = team_service.get_team_by_name(participant_1)
        participant_1 = participant_1.team_name

        participant_2 = team_service.get_team_by_name(participant_2)
        participant_2 = participant_2.team_name

    match = match_service.create_match(match_format, game_type, sport, participant_1,
            participant_2, user.full_name, date, tournament_name)
    output.append(f'-= {participant_1} vs {participant_2} =-')
    output.append(match)

    return [el for el in output]



" 4. ENTER MATCH WINNER"
@matches_router.put('/')
def enter_match_winner(token: str, match_id: int,
                       p1_name: str = Query(description='Enter participant 1 name'),
                       p1_score: float = Query(description='Enter participant 1 score'),
                       p2_name: str = Query(description='Enter participant 2 name'),
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

    if match.participant_1 != p1_name and match.participant_2 != p2_name:
        return JSONResponse(status_code=400, content=f"Wrong participants names")

    participant_1 = player_service.get_player_by_full_name(match.participant_1)
    participant_2 = player_service.get_player_by_full_name(match.participant_2)
    winner = match_service.enter_match_winner(match, participant_1, p1_score, participant_2, p2_score)

    return winner




" 5. DELETE A MATCH"
@matches_router.delete('/{id}')
def delete_match(id: int, token: str):
    user = get_user_or_raise_401(token)
    if not (User.is_director(user) or User.is_admin(user)):
        return JSONResponse(status_code=403, content='Only Admin and Director can delete a match')

    match = match_service.get_match_by_id(id)
    if not match:
        return JSONResponse(status_code=404, content=f'There is no match with id {id}.')

    result = match_service.delete_match(id)
    return result



" 5.1. DELETE MATCHES BY TOURNAMENT"
@matches_router.delete('/{title}/matches')
def delete_matches_by_tournament(title: str, token: str):
    user = get_user_or_raise_401(token)
    if not (User.is_director(user) or User.is_admin(user)):
        return JSONResponse(status_code=403, content='Only Admin and Director can delete a match')

    output = []
    output.append({'message': f'All matches from tournament {title} has been deleted'})
    matches = match_service.get_matches_by_tournament(title)
    for match in matches:
        result = match_service.delete_match(match.id)
        output.append(result)
    return output






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


