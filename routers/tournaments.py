from fastapi import APIRouter, Query, Header, Form
from fastapi.responses import JSONResponse
from services import  tournament_service, shared_service, match_service, team_service, player_service
from authentication.authenticator import get_user_or_raise_401
from my_models.model_user import User
from my_models.model_tournament import sport_list
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




" 3. CREATE TOURNAMENT"
@tournaments_router.post('/create')
def create_tournament(token: str = Header(),
                      title: str = Query(min_length=5),
                      number_participants: int = Form(..., enum=[4, 8, 16, 32, 64, 128]),
                      t_format: str = Form(..., enum=['knockout', 'league']),
                      match_format: str = Form(..., enum=['time limit', 'score limit']),
                      sport: str = Form(..., enum=sport_list),
                      game_type: str = Form(..., enum=['one on one', 'team game']),
                      date: str = Query(description='write date in format yyyy-mm-dd'),
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
def add_participant_to_tournament(title: str, participant: str, token):
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
            return JSONResponse(status_code=400, content=f'{team.name} is already in {tournament.title}')

        output.append(tournament_service.add_team(team, tournament))

    output.append(tournament_service.need_or_complete(tournament, table))
    return output




" 5. DELETE A TOURNAMENT"
@tournaments_router.delete('/{title}')
def delete_tournament_by_title(title: str, token: str):
    creator = get_user_or_raise_401(token)
    if not (User.is_director(creator) or User.is_admin(creator)):
        return JSONResponse(status_code=403, content='Only Admin and Director can create a match')

    tournament = tournament_service.get_tournament_by_title(title)
    if not tournament:
        return JSONResponse(status_code=404, content=f'{title} not found')

    tournament_service.delete_tournament_by_title(tournament.title, tournament.game_type)
    return {'message': f'{title} has been deleted.'}



" 6. CREATE STAGE"
@tournaments_router.post('/stage/{title}')
def create_tournament_stage(title: str, token: str):
    creator = get_user_or_raise_401(token)
    if not (User.is_director(creator) or User.is_admin(creator)):
        return JSONResponse(status_code=403, content='Only Admin and Director can create a match')

    tournament = tournament_service.get_tournament_by_title(title)
    if not tournament:
        return JSONResponse(status_code=404, content=f'{title} not found')

    stage = tournament_service.create_stage(tournament)
    return stage




"REMOVE PARTICIPANT"


"UPDATE TOURNAMENT"


"""

1 добавям участници



IF KNOCKOUT:
    number_of_tp = [4, 8, 16, 32, 64, 128] == stage(2, 3, 4, 5, 6, 7)
        
    # choose points range
        points_range = [0, 100]
        
    # arrange matches
        order = { match_1: [tp4, tp2], match_2:[tp1, tp3] }
            
        First = random.choice(included_teams) # tp4
        included_teams.remove(tp4)
        
        Second = random.choice(included_teams) # tp2
        included_teams.remove(tp2)
        
        order[match] = [First, Second]
    
    
    # play matches     
        play_match(First, Second)
        
    # calculate points
        First.match_points = random.choice(points_range)
        Second.match_points = random.choice(points_range)
        
        First.tournament_points += results
        Second.tournament_points += results
        
        statistics = insert_query(tournament_name, match_id, First.name, First.score, Second.name, Second.score)  
        
        
        


IF LEAGUE:  (all against all)
    # choose points range
        points_range = [0, 1, 3]
        
    # arrange matches
        played_matches = { match_1:[tp1, tp2], match_2:[tp1, tp3], match_3[tp2, tp3] }
        for First in teams:
            for Second in teams:
                if First == Second:
                    continue
                for value in played_matches.value():
                    if (First and Second) not in value:
          
    # play matches     
        play_match(First, Second)
        
    # calculate points
        First.match_points = random.choice(points_range)
            if First.match_points = 3:
                Second.match_points = 0
            elif First.match_points = 0
                Second.match_points = 3
            else: 
                First.match_points = 1
                Second.match_points = 1
                
        First.tournament_points += results
        Second.tournament_points += results
        
        statistics = insert_query(tournament_name, match_id, First.name, First.score, Second.name, Second.score)  
                
        winner = max( 1.score, 2.score, 3.score )
"""





# def generate_unique_pairs(numbers):
#     unique_pairs = set()
#     for i in range(len(numbers)):
#         for j in range(i + 1, len(numbers)):
#             unique_pairs.add((numbers[i], numbers[j]))
#
#     return list(unique_pairs)
#
# # Пример за използване:
# numbers = [1, 2, 3, 4, 5, 6, 7]
# result = generate_unique_pairs(numbers)
# print(result)





