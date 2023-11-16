from pydantic import constr
from data.database import insert_query
from my_models.model_tournament import Tournament



def create_tournament(title: str,
                      format: constr(pattern='^knockout|league$'),
                      date: str,
                      prize: int,
                      creator: str):
    generated_tournament =  insert_query(
        '''INSERT INTO tournaments (title, format, date, prize, players, creator)
           VALUE (?, ?, ?, ?, ?, ?)''', (title, format, date, prize, creator))

    result = Tournament(id = generated_tournament,
                        title = title,
                        format = format,
                        date = date,
                        prize = prize,
                        creator = creator)
    return result