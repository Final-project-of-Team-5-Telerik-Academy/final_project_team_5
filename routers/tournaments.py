from fastapi import APIRouter, Query, Header, Form
from fastapi.responses import JSONResponse
from services import  date_service, tournament_service, match_service, shared_service, player_service, team_service
from authentication.authenticator import get_user_or_raise_401, get_user_from_token
from pydantic import constr
from my_models.model_user import User
from datetime import datetime



tournaments_router = APIRouter(prefix='/tournaments', tags=['Tournaments'])


"CREATE TOURNAMENT"
@tournaments_router.post('/create')
def create_tournament(token: str = Header(), title: str = Query(min_length=5),
                      format: str = Form(..., description="Select an option",
                                         example='knockout', enum=['knockout', 'league']),
                      game_type: str = Form(..., description="Select an option",
                                            example='players', enum=['one on one', 'team game']),
                      number_participants: int = Form(..., description='Select number participants',
                                                      example=8, enum=[4, 8, 16, 32, 64, 128]),
                      date: str = Query(description='write date in format yyyy-mm-dd'),
                      prize: int = Query(gt=-1)):

# check if authenticated and role
    creator = get_user_or_raise_401(token)
    if not (User.is_director(creator) or User.is_admin(creator)):
        return JSONResponse(status_code=403, content='Only Admin and Director can create a match')

# check if the date is in the future
    if not date_service.date_is_in_future(date):
        today = date_service.current_date()
        return JSONResponse(status_code=400, content=f"Today is {today}. You must choose date in th future")

# creating new tournament
    date = datetime.strptime(date, "%Y-%m-%d").date()
    new_tournament = tournament_service.create_tournament(
        title, format, date, prize, game_type, creator, number_participants)

    return new_tournament



"ADD PARTICIPANTS TO TOURNAMENT"
@tournaments_router.put('/add/{t_title}/{participant}')
def add_participant_to_tournament(t_title: str, participant: str, token):
    tournament = tournament_service.get_tournament_by_title(t_title)

# check if authenticated
    user = get_user_or_raise_401(token)

# check admin or creator
    current_table = 'tournaments'
    creator_name = shared_service.get_creator_full_name(current_table, t_title)
    if not (user.full_name == creator_name or User.is_admin(user)):
        return JSONResponse(status_code=403, content='Only Admin and creator can assign players to match')

# check if tournament exists
    if not tournament:
        return JSONResponse(status_code=404, content=f'The tournament {t_title} does not exist.')

# get game format and tournament object
    game_type = tournament_service.get_game_type(t_title)

# check if tournament is finished
    if tournament.is_finished:
        return f'the tournament {tournament.title} is finished.'

# if game type is One on One
    if game_type == 'one on one':

    # check if player exists
        player = player_service.get_player_by_full_name(participant)
        if player is None:
            return JSONResponse(status_code=404, content=f'Player {participant} not found.')

    # check if player is already added
        if tournament_service.is_player_in_tournament(player.id, tournament.id):
            return f'{player.full_name} is already in {tournament.title}'

        # player = player_service.get_player_by_full_name(participant)
        result = tournament_service.add_participant(player, tournament)
        return result


    # if game type is Team game     TODO:
    #     elif game_type == 'team game':
    #     # check if team exists
    #         if not team_service.team_exists(participant):
    #             return JSONResponse(status_code=404, content=f'Team {participant} not found.')




"""
Tournament(BaseModel):


IF KNOCKOUT:
    number_of_tp = [4, 8, 16, 32, 64, 128] == circles(2, 3, 4, 5, 6, 7)
        
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





