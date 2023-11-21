from fastapi import APIRouter, Query, Header, Form
from fastapi.responses import JSONResponse
from services import player_service, statistic_service


statistics_router = APIRouter(prefix='/statistics', tags=['Statistics'])


@statistics_router.get('/')
def get_players_statistics(tp_name: str = Query(description='type a team or player name')):

    existing_player = player_service.get_player_by_full_name(tp_name)
    if existing_player is None:
        return JSONResponse(status_code=404, content=f'{existing_player} is not found')

    result = statistic_service.get_player_statistics(existing_player.full_name)
    return result