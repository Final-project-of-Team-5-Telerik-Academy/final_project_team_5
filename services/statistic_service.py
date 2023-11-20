from data.database import read_query
from fastapi.responses import JSONResponse



def get_player_statistics(player_name:str):
    all_matches = read_query('''SELECT player_name, opponent_name, win, loss, matches_id, tournament_name 
                            FROM players_has_matches WHERE player_name = ?''', (player_name,))
    if len(all_matches) == 0:
        return JSONResponse(status_code=404, content=f'{player_name} has no statistics yet.')

    wins_data = read_query('SELECT win FROM players_has_matches WHERE player_name = ?', (player_name,))
    losses_data = read_query('SELECT loss FROM players_has_matches WHERE player_name = ?', (player_name,))
    tournaments_played_data = read_query('SELECT tournament_name FROM players_has_matches WHERE player_name = ?', (player_name,))
    tournaments_trophy_data = read_query('SELECT tournament_trophy FROM players_has_matches WHERE player_name = ?', (player_name,))
    most_often_played_opponent_data = read_query(f'''SELECT opponent_name, COUNT(opponent_name) AS occurrence_count
                                                FROM players_has_matches WHERE opponent_name <> '{player_name}'
                                                GROUP BY opponent_name ORDER BY occurrence_count DESC LIMIT 1''', (player_name,))


    wins = sum([el[0] for el in wins_data])
    losses = sum([el[0] for el in losses_data])
    tournaments_played = len([el[0] for el in tournaments_played_data if el[0] != 'not part of a tournament'])
    tournaments_trophy = sum([el[0] for el in tournaments_trophy_data])
    most_often_played_opponent = most_often_played_opponent_data[0][0]
    games_against_him = most_often_played_opponent_data[0][1]


    result = []
    result.append('-= SUMMARY =-')
    header = {'name': f'{player_name}',
              'total wins': wins,
              'total losses': losses,
              'tournaments played': tournaments_played,
              'tournaments trophy': tournaments_trophy,
              'most often played opponent': most_often_played_opponent,
              'games_against_him': games_against_him
              }
    result.append(header)
    result.append('-= MATCHES LIST =-')

    for row in all_matches:
        player_name= row[0]
        opponent_name = row[1]
        win = row [2]
        loss = row[3]
        matches_id = row[4]
        tournament_name = row[5]
        data_dict = {
            'game': f'{player_name} vs {opponent_name}',
            'winner': f'{player_name if win==1 else opponent_name}',
            'match id': matches_id,
            'tournament name': f"{tournament_name if tournament_name else 'not part of a tournament'}"
        }
        result.append(data_dict)

    return result