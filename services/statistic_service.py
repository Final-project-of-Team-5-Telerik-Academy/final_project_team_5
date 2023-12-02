from data.database import read_query
from fastapi.responses import JSONResponse




"TEAM STATISTICS"
def get_single_player_team_statistics(name:str, wanted_matches: str, p_type: str):
    all_matches = read_query(f'''SELECT {p_type}_name, opponent_name, win, loss, matches_id, tournament_name, date 
                            FROM {p_type}s_statistics WHERE {p_type}_name = ? ORDER BY date''', (name,))
    if len(all_matches) == 0:
        return JSONResponse(status_code=404, content=f'{name} has no statistics yet.')

    wins_data = read_query(f'SELECT win FROM {p_type}s_statistics WHERE {p_type}_name = ?', (name,))
    losses_data = read_query(f'SELECT loss FROM {p_type}s_statistics WHERE {p_type}_name = ?', (name,))
    tournaments_played_data = read_query(f'''SELECT COUNT(*) FROM {p_type}s_statistics 
                                         WHERE tournament_name is not NULL AND {p_type}_name = ?''',
                                         (name,))
    tournaments_trophy_data = read_query(f'''SELECT tournament_trophy FROM {p_type}s_statistics 
                                         WHERE {p_type}_name = ?''', (name,))
    most_often_played_opponent_data = read_query(f'''SELECT opponent_name, COUNT(opponent_name) AS occurrence_count
                                                FROM {p_type}s_statistics WHERE opponent_name <> ?
                                                GROUP BY opponent_name ORDER BY occurrence_count DESC LIMIT 1''',
                                                 (name,))
    best_opponent_data = read_query(f'''SELECT opponent_name, COUNT(*) AS win_count FROM {p_type}s_statistics
                                        WHERE {p_type}_name = '{name}' AND win = 1 GROUP BY opponent_name 
                                        ORDER BY win_count DESC LIMIT 1''')
    worst_opponent_data = read_query(f'''SELECT opponent_name, COUNT(*) AS loss_count FROM {p_type}s_statistics
                                        WHERE {p_type}_name = '{name}' AND loss = 1 GROUP BY opponent_name 
                                        ORDER BY loss_count DESC LIMIT 1''')

    wins = sum([el[0] for el in wins_data])
    losses = sum([el[0] for el in losses_data])

    tournaments_played = tournaments_played_data[0][0]
    tournaments_trophy = sum([el[0] for el in tournaments_trophy_data])

    most_often_played_opponent = most_often_played_opponent_data[0][0]
    games_against_most_often = most_often_played_opponent_data[0][1]

    best_opponent = best_opponent_data[0][0]
    games_against_best_opponent = best_opponent_data[0][1]

    worst_opponent = worst_opponent_data[0][0]
    games_against_worst_opponent = worst_opponent_data[0][1]

    results_list = []
    results_list.append('-= SUMMARY =-')
    header = {'name': f'{name}',
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




def all_players_statistics(sort: str, order: str):
    row_data = read_query(
        f'''SELECT p.id, p.full_name, p.country, p.sports_club, p.is_active,
        SUM(ps.win) AS wins,
        SUM(ps.loss) AS losses,
        COUNT(DISTINCT ps.matches_id) AS matches,
        COUNT(DISTINCT ps.tournament_name) AS tournaments_played,
        SUM(ps.tournament_trophy) AS tournaments_wins
        FROM players p
        LEFT JOIN players_statistics ps ON p.id = ps.players_id
        GROUP BY p.id, p.full_name, p.country, p.sports_club, p.is_active
        ORDER BY {sort} {'ASC' if order == 'ascending' else 'DESC'}''')

    data = []
    for row in row_data:
        player_id = row[0]
        player_name = row[1]
        country = row[2]
        sports_club = row[3]
        is_active = ('yes' if row [4] == 0 else 'no')
        win = (0 if row[5] is None else row[5])
        loss = (0 if row[6] is None else row[6])
        matches = (0 if row[7] is None else row[7])
        tournaments = row[8]
        trophies = (0 if row[9] is None else row[9])

        data_dict = {
            'id':  player_id,
            'name': player_name,
            'country': country,
            'sports club': sports_club,
            'is active': is_active,
            'win': win,
            'loss': loss,
            'matches': matches,
            'tournaments': tournaments,
            'trophies': trophies}
        data.append(data_dict)

    return data



def all_teams_statistics(sort: str, order: str):
    row_data = read_query(
        f'''SELECT t.id, t.team_name
        SUM(ts.win) AS wins
        SUM(ts.loss) AS losses
        COUNT(DISTINCT ts.matches_id) AS matches,
        COUNT(DISTINCT ts.tournament_name) AS tournaments_played,
        SUM(ts.tournament_trophy) AS tournaments_wins
        FROM teams t
        LEFT JOIN teams_statistics ps ON t.id = ts.teams_id
        GROUP BY t.id, t.team_name
        ORDER BY {sort} {'ASC' if order == 'ascending' else 'DESC'}''')

    data = []
    for row in row_data:
        team_id = row[0]
        team_name = row[1]
        win = (0 if row[5] is None else row[5])
        loss = (0 if row[6] is None else row[6])
        matches = (0 if row[7] is None else row[7])
        tournaments = row[8]
        trophies = (0 if row[9] is None else row[9])

        data_dict = {
            'id':  team_id,
            'name': team_name,
            'win': win,
            'loss': loss,
            'matches': matches,
            'tournaments': tournaments,
            'trophies': trophies}
        data.append(data_dict)

    return data


