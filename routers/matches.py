from fastapi import APIRouter, Query, Form
from fastapi.responses import JSONResponse
from authentication.authenticator import get_user_or_raise_401
from services import shared_service, tournament_service, player_service, match_service, email_service, user_service
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
    if not result:
        return JSONResponse(status_code=404, content=f"There are no matches for {title}.")
    return result




" 2. VIEW MATCH BY ID"
@matches_router.get('/{id}', description='You can view all matches')
def view_match_by_id(id_m: int):
    result = match_service.get_match_by_id(id_m)
    if not result:
        return JSONResponse(status_code=404, content=f'There is no match with id {id_m}.')
    return result




" 3. CREATE MATCH"
@matches_router.post('/create/{match}', description='You can create new match')
def create_match(token: str,
                 game_type: str = Form('one on one', enum=['one on one', 'team game']),
                 sport: str = Form(..., enum=sports_list),
                 match_format: str = Form('time limit', enum=['time limit', 'score limit']),
                 participant_1: str = Query(),
                 participant_2: str = Query(),
                 date: str = Query(description='write date in format yyyy-m-d'),
                 tournament_name: str = Query(default='not part of a tournament')):

# check if authenticated and role
    user = get_user_or_raise_401(token)
    if not (User.is_director(user) or User.is_admin(user)):
        return JSONResponse(status_code=403, content='Only Admin and Director can create a match')

    shared_service.check_date_format(date)
    date = datetime.strptime(date, "%Y-%m-%d").date()

    output = []
    if game_type == 'one on one':
# ONE ON ONE
# player 1
        existing_player = match_service.get_player_by_full_name_v2(participant_1)
        if existing_player is None:
            participant_1 = player_service.create_player(participant_1, 'add country', 'add sports club')
            participant_1 = participant_1.full_name
            output.append({'warning': f'{participant_1} is new to the system. We have created a profile for him but it needs to be completed'})
        else:
            if existing_player.is_active == 0:  # 1 when player is active, 0 when player is not active
                return {'message': f'{existing_player.full_name} is not active player.'}

            users_account = user_service.players_id_exists_in_users(existing_player.id, existing_player.full_name)
            if users_account is not None:
                email_service.send_email(users_account.email, 'added_to_match')

# player 2
        existing_player = match_service.get_player_by_full_name_v2(participant_2)
        if existing_player is None:
            participant_2 = player_service.create_player(participant_2, 'add country', 'add sports club')
            participant_2 = participant_2.full_name
            output.append({'warning': f'{participant_2} is new to the system. We have created a profile for him but it needs to be completed'})
        else:
            if existing_player.is_active == 0:  # 1 when player is active, 0 when player is not active
                return {'message': f'{existing_player.full_name} is not active player.'}

            users_account = user_service.players_id_exists_in_users(existing_player.id, existing_player.full_name)
            if users_account is not None:
                email_service.send_email(users_account.email, 'added_to_match')


# TEAM GAME
    elif game_type == 'team game':
        existing_team = match_service.get_team_by_name_v2(participant_1)
        if not existing_team:
            return JSONResponse(status_code=404, content=f'Team {participant_1} does not exist in te system')
        participant_1 = existing_team.team_name

        existing_team = match_service.get_team_by_name_v2(participant_2)
        if not existing_team:
            return JSONResponse(status_code=404, content=f'Team {participant_2} does not exist in te system')
        participant_2 = existing_team.team_name

    if participant_1 == participant_2:
        return JSONResponse(status_code=400, content='The participants must be different .')

    match = match_service.create_match(match_format, game_type, sport, participant_1,
                                       participant_2, user.full_name, date, tournament_name)
    output.append(f'-= {participant_1} vs {participant_2} =-')
    output.append(match)

    return [el for el in output]




" 4. ENTER MATCH WINNER"
@matches_router.put('/')
def enter_match_winner(token: str, match_id: int,
                       p1_score = Query(description='Enter participant 1 score'),
                       p2_score = Query(description='Enter participant 2 score')):

    user = get_user_or_raise_401(token)
    if not (User.is_director(user) or User.is_admin(user)):
        return JSONResponse(status_code=403, content='Only Admin and Director can create a match')

    match = match_service.get_match_by_id(match_id)
    if  match is None:
        return JSONResponse(status_code=404, content='There is no match with that id')

    if match.winner != 'not played':
        return JSONResponse(status_code=400,
            content=f'The winner of match {match.id} is already set to {match.winner}.')

    winner = match_service.enter_match_winner(match, p1_score, p2_score)
    return winner




" 5. DELETE A MATCH"
@matches_router.delete('/{id}')
def delete_match(id_m: int, token: str):
    user = get_user_or_raise_401(token)
    if not User.is_admin(user):
        return JSONResponse(status_code=403, content='Only Admin can delete a match')

    match = match_service.get_match_by_id(id_m)
    if not match:
        return JSONResponse(status_code=404, content=f'There is no match with id {id_m}.')

    result = match_service.delete_match(id_m)
    return result



" 5.1. DELETE MATCHES BY TOURNAMENT"
@matches_router.delete('/{title}/matches')
def delete_matches_by_tournament(title: str, token: str):
    user = get_user_or_raise_401(token)
    if not (User.is_director(user) or User.is_admin(user)):
        return JSONResponse(status_code=403, content='Only Admin and Director can delete a match')

    output = list()
    output.append({'message': f'All matches from tournament {title} has been deleted'})
    matches = match_service.get_matches_by_tournament(title)
    if not matches:
        return JSONResponse(status_code=404, content=f"There are no matches for tournament '{title}'")
    for match in matches:
        result = match_service.delete_match(match.id)
        output.append(result)
    return output




" 6. MATCHES SIMULATIONS"
@matches_router.get('/simulations/')
def matches_simulations(token: str):
    creator = get_user_or_raise_401(token)
    if not (User.is_director(creator) or User.is_admin(creator)):
        return JSONResponse(status_code=403, content='Only Admin and Director can simulate a matches results')

    output = []
    result = match_service.matches_simulations()
    if not result:
        return {'message': 'Not available matches for simulation'}
    else:
        output.append('-= MATCHES SIMULATIONS RESULTS =-')
        output.append(result)
        return output



