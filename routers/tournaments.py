from fastapi import APIRouter, Query, Header, Form
from fastapi.responses import JSONResponse
from services import tournament_service, match_service, shared_service, player_service, user_service, email_service
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
def view_tournament_by_title(title: str):
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

    output = list()
    output.append(tournament_service.get_tournament_by_title(title))
    output.append('-= PARTICIPANTS =-')

    participants = tournament_service.get_participants(tournament)
    if not participants:
        return {'message': f'Tournament {title} has no added participants'}

    output.append(participants)
    return output




" 3. CREATE TOURNAMENT"
@tournaments_router.post('/create')
def create_tournament(token: str = Header(),
                      title: str = Query(min_length=5),
                      number_participants: int = Form(..., enum=[4, 8, 16, 32, 64, 128]),
                      t_format: str = Form('league', enum=['league', 'knockout']),
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
        return JSONResponse(status_code=404, content=f"The tournament '{title}' not found")
    if tournament.winner != 'Not finished yet':
        return f'the tournament {tournament.title} is finished.'


    output = list()

# ONE ON ONE GAME
    if tournament.game_type == 'one on one':
        table = 'players'
        enough = tournament_service.enough_participants(tournament)
        if enough:
            return enough

        player = match_service.get_player_by_full_name_v2(participant)
        if player is None:
            player = player_service.create_player(participant, 'add country', 'add sports club')
            output.append({'warning': f'{participant} is new to the system. We have created a profile for him but it needs to be completed'})

        elif tournament_service.is_player_in_tournament(player.id, tournament.id, table):
            return JSONResponse(status_code=400, content=f'{player.full_name} is already in {tournament.title}')

        if player.is_active == 0:  # 1 when player is active, 0 when player is not active
            return {'message': f'{player.full_name} is not active player.'}

        result = tournament_service.add_player_to_tournament(player, tournament)
        output.append(result)

        participants = tournament_service.get_participants(tournament)
        
        for p in participants:
            users_account = user_service.players_id_exists_in_users(p['id'], p['name'])
            if users_account is not None:
                email_service.send_email(users_account.email, 'added_to_tournament')
        
        difference = tournament.number_participants - len(participants)
        if difference > 0:
            output.append(f'you need {difference} participants to complete the tournament.')
            return output

# TEAMS GAME
    elif tournament.game_type == 'team game':
        table = 'teams'
        team = match_service.get_team_by_name_v2(participant)
        if team is None:
            return JSONResponse(status_code=404, content=f'Team {participant} not found.')
        if tournament_service.is_player_in_tournament(team.id, tournament.id, table):
            return JSONResponse(status_code=400, content=f'{team.team_name} is already in {tournament.title}')

        output.append(tournament_service.add_team_to_tournament(team, tournament))

    output.append(tournament_service.need_or_complete(tournament))
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




" 6. ARRANGE TOURNAMENT MATCHES"
@tournaments_router.post('/stage/{title}')
def arrange_tournament_matches(title: str, token: str, matches_per_day: int | None = None):
    creator = get_user_or_raise_401(token)
    if not (User.is_director(creator) or User.is_admin(creator)):
        return JSONResponse(status_code=403, content='Only Admin and Director can create a match')

    tournament = tournament_service.get_tournament_by_title(title)
    if not tournament:
        return JSONResponse(status_code=404, content=f'{title} not found')
    if tournament.is_completed == 0:
        return JSONResponse(status_code=400, content=f'{title} is not completed. You must add participants.')


# KNOCKOUT
    if tournament.t_format == 'knockout':
        stage = tournament_service.create_knockout_stage(tournament)
        return stage

# LEAGUE
    elif tournament.t_format == 'league':
        league = tournament_service.arrange_league(tournament, matches_per_day)
        return league




" 8. ENTER LEAGUE WINNER"
@tournaments_router.post('/{title}/league/results')
def set_league_tournament_winner(title: str, token: str):
    creator = get_user_or_raise_401(token)
    if not User.is_admin(creator):
        return JSONResponse(status_code=403, content='Only Admin can create a match')

    tournament = tournament_service.get_tournament_by_title(title)
    if not tournament:
        return JSONResponse(status_code=404, content=f'{title} not found')
    if tournament.t_format != 'league':
        return JSONResponse(status_code=400, content="This tournament format is not 'league'")

    matches = match_service.get_matches_by_tournament(title)
    for match in matches:
        if match.winner == 'not played':
            return JSONResponse(status_code=400, content='All matches must be finished before calculation')
    if tournament_service.has_winner(title) != 'Not finished yet':
        return JSONResponse(status_code=400, content='The tournament si already finished')

    if tournament.game_type == 'one on one':
        p_type = 'player'
    else:
        p_type = 'team'

    output = []
    score_data = tournament_service.get_league_participants_points_for_tournament(tournament)
    winner = score_data[0]
    winner_n = str(winner.values())
    winner_name = str(winner_n[14:-3])
    tournament_service.set_winner(title, winner_name)

    output.append(f'-= {tournament.title} RESULTS =-')
    output.append(tournament)
    output.append(f'The winner is: {winner_name}!')
    output.append(score_data)
    tournament_service.add_tournament_trophy(winner_name, p_type, tournament)

    return output






