from fastapi import APIRouter, Query, Form
from fastapi.responses import JSONResponse
from services import player_service, statistic_service


statistics_router = APIRouter(prefix='/statistics', tags=['Statistics'])


@statistics_router.get('/{player}')
def player_statistics(name: str = Query(description="type team or player name", default='Jim Halpert'),
                      matches: str = Query(description='filter by: all / wins / losses', default='all')):

    existing_player = player_service.get_player_by_full_name(name)
    if existing_player is None:
        return JSONResponse(status_code=404, content=f'{existing_player} is not found')

    result = statistic_service.get_player_statistics(existing_player.full_name, matches)
    return result



@statistics_router.put('/players_ranklist')
def players_ranklist(sort: str = Form(..., description="Select an option", example='most personal wins',
                                      enum=['personal wins', 'tournament wins', 'played matches one on one', 'played in tournaments']),
                     order_date: str = Form(..., description='Order by date', example='ascending', enum=['ascending', 'descending']) ):
    result = statistic_service.players_ranklist(sort, order_date)















