from data.database import read_query
from fastapi.responses import JSONResponse



def get_player_statistics(player_name:str, wanted_matches: str):
    all_matches = read_query('''SELECT player_name, opponent_name, win, loss, matches_id, tournament_name, date 
                            FROM players_statistics WHERE player_name = ? ORDER BY date''', (player_name,))
    if len(all_matches) == 0:
        return JSONResponse(status_code=404, content=f'{player_name} has no statistics yet.')

    wins_data = read_query('SELECT win FROM players_statistics WHERE player_name = ?', (player_name,))
    losses_data = read_query('SELECT loss FROM players_statistics WHERE player_name = ?', (player_name,))
    tournaments_played_data = read_query('SELECT tournament_name FROM players_statistics WHERE player_name = ?', (player_name,))
    tournaments_trophy_data = read_query('SELECT tournament_trophy FROM players_statistics WHERE player_name = ?', (player_name,))
    most_often_played_opponent_data = read_query(f'''SELECT opponent_name, COUNT(opponent_name) AS occurrence_count
                                                FROM players_statistics WHERE opponent_name <> ?
                                                GROUP BY opponent_name ORDER BY occurrence_count DESC LIMIT 1''', (player_name,))
    best_opponent_data = read_query(f'''SELECT opponent_name, COUNT(*) AS win_count FROM players_statistics
                                        WHERE player_name = '{player_name}' AND win = 1 GROUP BY opponent_name 
                                        ORDER BY win_count DESC LIMIT 1''')
    worst_opponent_data = read_query(f'''SELECT opponent_name, COUNT(*) AS loss_count FROM players_statistics
                                        WHERE player_name = '{player_name}' AND loss = 1 GROUP BY opponent_name 
                                        ORDER BY loss_count DESC LIMIT 1''')

    wins = sum([el[0] for el in wins_data])
    losses = sum([el[0] for el in losses_data])

    tournaments_played = len([el[0] for el in tournaments_played_data if el[0] != 'not part of a tournament'])
    tournaments_trophy = sum([el[0] for el in tournaments_trophy_data])

    most_often_played_opponent = most_often_played_opponent_data[0][0]
    games_against_most_often = most_often_played_opponent_data[0][1]

    best_opponent = best_opponent_data[0][0]
    games_against_best_opponent = best_opponent_data[0][1]

    worst_opponent = worst_opponent_data[0][0]
    games_against_worst_opponent = worst_opponent_data[0][1]

    results_list = []
    results_list.append('-= SUMMARY =-')
    header = {'name': f'{player_name}',
              'total wins': wins,
              'total losses': losses,
              'tournaments played': tournaments_played,
              'tournaments trophy': tournaments_trophy,
              'most often opponent': most_often_played_opponent,
              'games against most often opponent': games_against_most_often,
              'best opponent': best_opponent,
              'games against best opponent': games_against_best_opponent,
              'worst opponent': worst_opponent,
              'games against worst opponent': games_against_worst_opponent
              }
    results_list.append(header)
    results_list.append('-= MATCHES LIST =-')


    if wanted_matches == 'all':
        all_matches = all_matches_convertor(all_matches)
        for el in all_matches:
            results_list.append(el)

    elif wanted_matches == 'wins':
        win_matches = wins_matches_convertor(all_matches)
        for el in win_matches:
            results_list.append(el)

    elif wanted_matches == 'losses':
        loss_matches = losses_matches_convertor(all_matches)
        for el in loss_matches:
            results_list.append(el)

    else:
        return JSONResponse(status_code=400, content="You can choose between: all / wins / losses.")

    return results_list



def all_matches_convertor(all_matches):
    data = []
    counter = 0
    for row in all_matches:
        counter += 1
        player_name = row[0]
        opponent_name = row[1]
        win = row[2]
        loss = row[3]
        matches_id = row[4]
        tournament_name = row[5]
        date = row[6]
        data_dict = {
            f"{player_name}'s match #": counter,
            'match': f'{player_name} vs {opponent_name}',
            'winner': f'{player_name if win == 1 else opponent_name}',
            'match id': matches_id,
            'tournament name': f"{tournament_name if tournament_name else 'not part of a tournament'}",
            'date': date
        }

        data.append(data_dict)
    return data



def wins_matches_convertor(all_matches):
    data = []
    for row in all_matches:
        if row[2] == 1:
            player_name = row[0]
            opponent_name = row[1]
            win = row[2]
            loss = row[3]
            matches_id = row[4]
            tournament_name = row[5]
            date = row[6]
            data_dict = {
                'match': f'{player_name} vs {opponent_name}',
                'winner': f'{player_name if win == 1 else opponent_name}',
                'match id': matches_id,
                'tournament name': f"{tournament_name if tournament_name else 'not part of a tournament'}",
                'date': date
            }
            data.append(data_dict)

    return data



def losses_matches_convertor(all_matches):
    data = []
    for row in all_matches:
        if row[2] == 0:
            player_name = row[0]
            opponent_name = row[1]
            win = row[2]
            loss = row[3]
            matches_id = row[4]
            tournament_name = row[5]
            data_dict = {
                'match': f'{player_name} vs {opponent_name}',
                'winner': f'{player_name if win == 1 else opponent_name}',
                'match id': matches_id,
                'tournament name': f"{tournament_name if tournament_name else 'not part of a tournament'}"}
            data.append(data_dict)

    return data



def players_ranklist(sort:str, order_date: str):
    where_clause = []
    sql = 'SELECT player_name, opponent_name, win, loss, matches_id, tournament_name, date FROM players_statistics'
    where_clause.append(sql)

    if sort == 'personal wins':
        where_clause.append('ORDER BY wins')

    elif sort == 'tournament wins':
        pass
    elif sort == 'played matches one on one':
        pass
    elif sort == 'played in tournaments':
        pass

    if order_date == 'ascending':
        where_clause.append('ASC')
    else:
        where_clause.append("DESC")
# tournaments'
