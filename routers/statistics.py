from fastapi import APIRouter, Form
from fastapi.responses import JSONResponse
from services import statistic_service, match_service


statistics_router = APIRouter(prefix='/statistics', tags=['Statistics'])


@statistics_router.put('/')
def single_player_or_team_statistics(name: str,
                         type: str = Form('player', enum=['player', 'team']),
                         matches: str = Form('all', enum=['all', 'wins', 'losses'])):

    if type == 'player':
        existing_player = match_service.get_player_by_full_name_v2(name)
        if existing_player is None:
            return JSONResponse(status_code=404, content=f'{name} is not found')
        participant_name = existing_player.full_name
    else:
        existing_team = match_service.get_team_by_name_v2(name)
        if existing_team is None:
            return JSONResponse(status_code=404, content=f'{name} is not found')
        participant_name = existing_team.team_name

    result = statistic_service.get_single_player_team_statistics(participant_name, matches, type)
    return result



@statistics_router.post('/')
def all_players_or_teams_statistics(type: str = Form('player', enum=['player', 'team']),
                                    sort: str = Form(..., enum=['wins', 'matches', 'tournaments_played', 'tournaments_wins']),
                                    order: str = Form(..., enum=['descending', 'ascending'])):

    if type == 'player':
        result = statistic_service.all_players_statistics(sort, order)
    else:   # TEAM
        result = statistic_service.all_teams_statistics(sort, order)
    return result







