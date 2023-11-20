from data.database import read_query
from fastapi.responses import JSONResponse



def get_player_statistics(player_name:str):
    all_matches = read_query('''SELECT player_name, opponent_name, win, loss, matches_id, tournament_name 
                            FROM players_has_matches WHERE player_name = ?''', (player_name,))
    wins_data = read_query('SELECT win FROM players_has_matches WHERE player_name = ?', (player_name,))
    losses_data = read_query('SELECT loss FROM players_has_matches WHERE player_name = ?', (player_name,))

    all_wins = sum(el for el in wins_data[0])
    all_losses = sum(el for el in losses_data[0])

    if not all_matches:
        return JSONResponse(status_code=404, content=f'{player_name} has no statistics yet.')

    result = []
    header = {'name': f'{player_name}',
              'total wins': f'{all_wins}',
              'total losses': f'{all_losses}'}
    result.append(header)

    for row in all_matches:

    data = read_query('''SELECT player_name, opponent_name, win, loss, matches_id, tournament_name 
                            FROM players_has_matches WHERE player_name = ?''', (player_name,))

    # return next((Player.from_query_result(*row) for row in data), None)
    if not data:
        return JSONResponse(status_code=404, content=f'{player_name} has no statistics yet.')

    result = []
    for row in data:
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