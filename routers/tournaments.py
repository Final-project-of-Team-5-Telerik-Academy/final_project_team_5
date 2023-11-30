from fastapi import APIRouter, Query, Header, Form
from fastapi.responses import JSONResponse
from services import  tournament_service, shared_service, match_service, team_service, player_service
from authentication.authenticator import get_user_or_raise_401
from my_models.model_user import User
from my_models.model_match import sports_list
from datetime import datetime



tournaments_router = APIRouter(prefix='/tournaments', tags=['Tournaments'])


" 1. VIEW ALL TOURNAMENTS"
@tournaments_router.post('/')
def view_all_tournaments(sort: str = Form('asc', enum=['asc', 'desc']),
                        status: str = Form('all', enum=['all', 'played', 'upcoming'])):

    result = tournament_service.get_tournaments(sort, status)
    return result




" 2. VIEW TOURNAMENT BY TITLE"
@tournaments_router.get('/{title}')
def get_tournament_by_title(title: str):
    tournament = tournament_service.get_tournament_by_title(title)
    if not tournament:
        return JSONResponse(status_code=404, content=f'{title} not found')
    return tournament




" 2.1. VIEW TOURNAMENT PARTICIPANTS"
@tournaments_router.get('/{title}/participants')
def view_tournament_participants(title: str):
    tournament = tournament_service.get_tournament_by_title(title)
    if not tournament:
        return JSONResponse(status_code=404, content=f'{title} not found')

    output = []
    output.append(tournament_service.get_tournament_by_title(title))
    output.append('-= PARTICIPANTS =-')
    output.append(tournament_service.get_participants(tournament))

    return output




" 3. CREATE TOURNAMENT"
@tournaments_router.post('/create')
def create_tournament(token: str = Header(),
                      title: str = Query(min_length=5),
                      number_participants: int = Form(..., enum=[4, 8, 16, 32, 64, 128]),
                      t_format: str = Form(..., enum=['knockout', 'league']),
                      match_format: str = Form(..., enum=['time limit', 'score limit']),
                      sport: str = Form(..., enum=sports_list),
                      game_type: str = Form(..., enum=['one on one', 'team game']),
                      date: str = Query(description='write date in format yyyy-m-d'),
                      prize: int = Query(gt=-1)):

    creator = get_user_or_raise_401(token)
    if not (User.is_director(creator) or User.is_admin(creator)):
        return JSONResponse(status_code=403, content='Only Admin and Director can create a match')

    shared_service.check_date_format(date)
    date = datetime.strptime(date, "%Y-%m-%d").date()

    if tournament_service.get_tournament_by_title(title):
        return JSONResponse(status_code=400, content=f"The name '{title}' already exists.")

    new_tournament = tournament_service.create_tournament(title, number_participants,
            t_format, match_format, sport, date, prize, game_type, creator)
    return new_tournament




" 4. ADD PARTICIPANTS TO TOURNAMENT"
@tournaments_router.put('/add/{t_title}/{participant}')
def add_participant_to_tournament(title: str, participant: str, token: str):
    user = get_user_or_raise_401(token)
    if not (User.is_director(user) or User.is_admin(user)):
        return JSONResponse(status_code=403, content='Only Admin and Director can create a match')

    tournament = tournament_service.get_tournament_by_title(title)
    if not tournament:
        return JSONResponse(status_code=404, content=f'{title} not found')
    if tournament.winner != 'Not finished yet':
        return f'the tournament {tournament.title} is finished.'

    table = None
    output = []
    if tournament.game_type == 'one on one':
        table = 'players'
        enough = tournament_service.enough_participants(tournament)
        if enough:
            return enough

        player = player_service.get_player_by_full_name(participant)
        if player is None:
            player = match_service.check_create_player(participant)
            output.append({'warning': f'{participant} is new to the system. We have created a profile for him but it needs to be completed'})

        elif tournament_service.is_player_in_tournament(player.id, tournament.id, table):
            return JSONResponse(status_code=400, content=f'{player.full_name} is already in {tournament.title}')

        output.append(tournament_service.add_player_to_tournament(player, tournament))


    elif tournament.game_type == 'team game':
        table = 'teams'
        team = team_service.get_team_by_name(participant)
        if team is None:
            return JSONResponse(status_code=404, content=f'Team {participant} not found.')
        if tournament_service.is_player_in_tournament(team.id, tournament.id, table):
            return JSONResponse(status_code=400, content=f'{team.team_name} is already in {tournament.title}')

        output.append(tournament_service.add_team(team, tournament))

    output.append(tournament_service.need_or_complete(tournament, table))
    return output




" 5. DELETE A TOURNAMENT"
@tournaments_router.delete('/{title}')
def delete_tournament_by_title(title: str, token: str):
    creator = get_user_or_raise_401(token)
    if not User.is_admin(creator):
        return JSONResponse(status_code=403, content='Only Admin can create a match')

    tournament = tournament_service.get_tournament_by_title(title)
    if not tournament:
        return JSONResponse(status_code=404, content=f'{title} not found')

    tournament_service.delete_tournament_by_title(tournament.title, tournament.game_type)
    return {'message': f'{title} has been deleted.'}




" 6. CREATE KNOCKOUT STAGE"
@tournaments_router.post('/stage/{title}')
def arrange_knockout_stage(title: str, token: str):
    creator = get_user_or_raise_401(token)
    if not (User.is_director(creator) or User.is_admin(creator)):
        return JSONResponse(status_code=403, content='Only Admin and Director can create a match')

    tournament = tournament_service.get_tournament_by_title(title)
    if not tournament:
        return JSONResponse(status_code=404, content=f'{title} not found')
    if tournament.t_format != 'knockout':
        return JSONResponse(status_code=400, content='knockout format is not aloud for tournament type "league"')

    stage = tournament_service.create_knockout_stage(tournament)
    return stage




" 7. ARRANGE LEAGUE"
@tournaments_router.post('/league/{title}')
def arrange_league(title: str, matches_per_days: int, token: str):
    creator = get_user_or_raise_401(token)
    if not (User.is_director(creator) or User.is_admin(creator)):
        return JSONResponse(status_code=403, content='Only Admin and Director can create a match')

    tournament = tournament_service.get_tournament_by_title(title)
    if not tournament:
        return JSONResponse(status_code=404, content=f'{title} not found')
    if tournament.t_format != 'league':
        return JSONResponse(status_code=400, content="League format is not aloud for tournament type 'knockout'")

    league = tournament_service.arrange_league(tournament, matches_per_days)
    return league




" 8. GET LEAGUE RESULTS"
@tournaments_router.get('/{title}/results')
def get_league_results(title: str):
    tournament = tournament_service.get_tournament_by_title(title)
    if tournament.t_format != 'league':
        return JSONResponse(status_code=400, content='This tournament format is not "league"')

    participants_list = tournament_service.get_participants(tournament)

    matches = match_service.get_matches_by_tournament(title)
    for match in matches:
        if match.winner == 'not played':
            return JSONResponse(status_code=400, content='All matches must be finished before calculation')

    score_data = match_service.get_participants_points_for_tournament(title)
    return score_data




" 8. TOURNAMENT SIMULATION"
@tournaments_router.get('/simulate/{title}')
def tournament_simulation(token: str, title: str):
    creator = get_user_or_raise_401(token)
    if not (User.is_director(creator) or User.is_admin(creator)):
        return JSONResponse(status_code=403, content='Only Admin and Director can simulate a matches results')

    tournament = tournament_service.get_tournament_by_title(title)
    output = []
    output.append(f'-= {tournament.title} SIMULATION RESULTS =-')

    if tournament.t_format == 'league':
        tournament_service.simulate_league_tournament(tournament)
        output.append(match_service.get_matches_by_tournament(title))

    elif tournament.t_format == 'knockout':
        tournament_service.simulate_knockout_tournament_matches(tournament)
        output.append(match_service.get_matches_by_tournament(title))

    return output




