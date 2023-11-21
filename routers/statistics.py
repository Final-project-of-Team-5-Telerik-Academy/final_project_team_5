from fastapi import APIRouter, Query, Header
from fastapi.responses import JSONResponse
from services import player_service, statistic_service


statistics_router = APIRouter(prefix='/statistics', tags=['Statistics'])


@statistics_router.get('/{tp_player}')
def get_statistics(tp_name: str = Query(description="type team or player name", default='Jim Halpert'),
                   matches: str = Query(description='filter by: all / wins / losses', default='all')):

    existing_player = player_service.get_player_by_full_name(tp_name)
    if existing_player is None:
        return JSONResponse(status_code=404, content=f'{existing_player} is not found')

    result = statistic_service.get_player_statistics(existing_player.full_name, matches)
    return result