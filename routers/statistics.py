from fastapi import APIRouter, Form
from fastapi.responses import JSONResponse
from services import statistic_service, match_service, tournament_service


statistics_router = APIRouter(prefix='/statistics', tags=['Statistics'])

'SINGLE PLAYER OR TEAM STATISCTICS'
@statistics_router.post('/single', description = "Giving an information about a player or team statisctic.")
def single_player_or_team_statistics(name: str,
                         p_type: str = Form('player', enum=['player', 'team']),
                         matches: str = Form('all', enum=['all', 'wins', 'losses'])):

    if p_type == 'player':
        existing_player = match_service.get_player_by_full_name_v2(name)
        if existing_player is None:
            return JSONResponse(status_code=404, content=f'{name} is not found!')
        participant_name = existing_player.full_name
    else:   # team
        existing_team = match_service.get_team_by_name_v2(name)
        if existing_team is None:
            return JSONResponse(status_code=404, content=f'The team {name} is not found!')
        participant_name = existing_team.team_name

    result = statistic_service.get_single_player_team_statistics(participant_name, matches, p_type)
    return result



@statistics_router.post('/all', description = "Giving an information about all players and teams in sorted order.")
def all_players_or_teams_statistics(p_type: str = Form('player', enum=['player', 'team']),
                                    sort: str = Form(..., enum=['wins', 'matches', 'tournaments_played', 'tournaments_wins']),
                                    order: str = Form(..., enum=['descending', 'ascending'])):

    if p_type == 'player':
        result = statistic_service.all_players_statistics(sort, order)
    else:   # TEAM
        result = statistic_service.all_teams_statistics(sort, order)
    return result



@statistics_router.post('/{title}', description = "Giving a statistic of all tournament results.")
def view_tournament_results(title: str):
    tournament = tournament_service.get_tournament_by_title(title)
    if not tournament:
        return JSONResponse(status_code=404, content=f'{title} not found!')

    output = []
    score_data = tournament_service.get_league_participants_points_for_tournament(tournament)
    output.append(f'-= {tournament.title} RESULTS =-')
    output.append(tournament)
    winner = score_data[0]
    winner_n = str(winner.values())
    winner_name = str(winner_n[14:-3])
    output.append(f'The winner is: {winner_name}!')
    output.append(score_data)

    return output





