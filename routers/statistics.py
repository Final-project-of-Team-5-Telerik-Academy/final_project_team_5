from fastapi import APIRouter, Query, Header, Form
from fastapi.responses import JSONResponse
from services import player_service, statistic_service


statistics_router = APIRouter(prefix='/statistics', tags=['Statistics'])


@statistics_router.put('/{player}')
def single_player_statistics(name: str = Query(description="type player name", default='Jim Halpert'),
                             matches: str = Form('all', enum=['all', 'wins', 'losses'])):

    existing_player = player_service.get_player_by_full_name(name)
    if existing_player is None:
        return JSONResponse(status_code=404, content=f'{existing_player} is not found')

    result = statistic_service.get_player_statistics(existing_player.full_name, matches)
    return result


@statistics_router.put('/{all_players}')
def all_players_statistics(sort: str = Form(..., enum=['wins', 'matches', 'tournaments_played', 'tournaments_win']),
                           order: str = Form(..., enum=['descending', 'ascending'])):
    result = statistic_service.all_players_statistics(sort, order)
    return result




