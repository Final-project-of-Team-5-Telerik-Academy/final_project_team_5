from fastapi import APIRouter, Query, Header, Form
from fastapi.responses import JSONResponse
from services import  date_service, tournament_service, match_service, shared_service, player_service, team_service
from authentication.authenticator import get_user_or_raise_401, get_user_from_token
from pydantic import constr
from my_models.model_user import User
from datetime import datetime



tournaments_router = APIRouter(prefix='/tournaments', tags=['Tournaments'])


'VIEW ALL TOURNAMENTS'
@tournaments_router.post('/')
def view_all_tournaments(sort: str = Form(..., description="Select an option",
                                  enum=['asc', 'desc']),
                        status: str = Form(..., description="Select an option",
                                  enum=['all', 'played', 'upcoming'])):

    result = tournament_service.get_tournaments(sort, status)
    return result


"VIEW TOURNAMENT BY TITLE"
@tournaments_router.get('/{title}')
def get_tournament_by_title(title: str):
    tournament = tournament_service.get_tournament_by_title(title)
    if not tournament:
        return JSONResponse(status_code=404, content=f'{title} not found')
    return tournament



"CREATE TOURNAMENT"
@tournaments_router.post('/create')
def create_tournament(token: str = Header(),
                      title: str = Query(min_length=5),
                      number_participants: int = Form(..., description="Select an option",
                                            enum=[4, 8, 16, 32, 64, 128]),
                      t_format: str = Form(..., description="Select an option",
                                            enum=['knockout', 'league']),
                      match_format: str = Form(..., description='Select an option',
                                               enum=['time limit', 'score limit']),
                      game_type: str = Form(..., description="Select an option",
                                            enum=['one on one', 'team game']),
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

# check title
    if tournament_service.get_tournament_by_title(title):
        return JSONResponse(status_code=400, content=f"The name '{title}' already exists.")

# creating new tournament
    date = datetime.strptime(date, "%Y-%m-%d").date()
    new_tournament = tournament_service.create_tournament(
        title, number_participants, t_format, match_format, date, prize, game_type, creator)

    return new_tournament



"ADD PARTICIPANTS TO TOURNAMENT"
@tournaments_router.put('/add/{t_title}/{participant}')
def add_participant_to_tournament(title: str, participant: str, token):
    tournament = tournament_service.get_tournament_by_title(title)
    if not tournament:
        return JSONResponse(status_code=404, content=f'{title} not found')
    if tournament.winner != 'Not finished yet':
        return f'the tournament {tournament.title} is finished.'

# check if authenticated admin or creator
    user = get_user_or_raise_401(token)
    current_table = 'tournaments'
    creator_name = shared_service.get_creator_full_name(current_table, title)
    if not (user.full_name == creator_name or User.is_admin(user)):
        return JSONResponse(status_code=403, content='Only Admin and creator can assign players to match')

# check number of participants is enough
    output = []

    participants = tournament_service.get_participant(tournament)
    difference = tournament.number_participants - len(participants)
    if difference > 0:
        output.append(f'you need {difference} participants to complete the tournament.')
    elif difference == 0:
        return JSONResponse(status_code=400, content=f'The tournament allows only {tournament.number_participants} participants. You have enough.')
    else:
        tournament_service.complete_tournament(title)
        return f'{tournament.title} is ready to begin.'

# game format and tournament object
    output = []
    if tournament.game_type == 'one on one':
        player = player_service.get_player_by_full_name(participant)
        if player is None:
            return JSONResponse(status_code=404, content=f'Player {participant} not found.')
        if tournament_service.is_player_in_tournament(player.id, tournament.id):
            return JSONResponse(status_code=400, content=f'{player.full_name} is already in {tournament.title}')
        if tournament_service.enough_participants(tournament):
            return JSONResponse(status_code=400, content=f'The tournament allows only {tournament.number_participants} participants.')

        result = tournament_service.add_player(player, tournament)
        output.append(result)

        participants = tournament_service.get_participant(tournament)
        difference = tournament.number_participants - len(participants)
        if difference > 0:
            output.append(f'you need {difference} participants to complete the tournament.')
            return output


    elif tournament.game_type == 'team game':
        team = team_service.get_team_by_name(participant)
        if team is None:
            return JSONResponse(status_code=404, content=f'Team {participant} not found.')
        if tournament_service.is_player_in_tournament(team.id, tournament.id):
            return JSONResponse(status_code=400, content=f'{team.name} is already in {tournament.title}')

        result = tournament_service.add_team(team, tournament)
        output.append(result)

    tournament_service.complete_tournament(title)
    output.append(f'{tournament.title} is ready to begin.')

    return output


"REMOVE PARTICIPANT"


"UPDATE TOURNAMENT"



"DELETE A TOURNAMENT"
@tournaments_router.delete('/{title}')
def delete_tournament_by_title(title: str, token: str):
    creator = get_user_or_raise_401(token)
    if not (User.is_director(creator) or User.is_admin(creator)):
        return JSONResponse(status_code=403, content='Only Admin and Director can create a match')

    tournament = tournament_service.get_tournament_by_title(title)
    if not tournament:
        return JSONResponse(status_code=404, content=f'{title} not found')
    tournament_service.delete_tournament_by_title(tournament.title, tournament.game_type)
    return f'{title} has been deleted.'



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





