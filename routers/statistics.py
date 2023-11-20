from fastapi import APIRouter, Query, Header, Form
from fastapi.responses import JSONResponse
from services import player_service, statistic_service


statistics_router = APIRouter(prefix='/statistics', tags=['Statistics'])


@statistics_router.get('/')
def get_players_statistics(player_name: str):
    existing_player = player_service.get_player_by_full_name(player_name)
    if existing_player is None:
        return JSONResponse(status_code=404, content=f'{existing_player} is not found')

    result = statistic_service.get_player_statistics(existing_player.full_name)
    return result