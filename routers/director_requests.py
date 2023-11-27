from fastapi import APIRouter, Header, Query, Form
from services import user_service
from my_models import countries, sport_clubs


director_requests_router = APIRouter(prefix='/director_requests', tags={'Director Requests'})


@director_requests_router.post('/', description="Please fill the form to create and send a request for creating a player with your names:")
def create_director_request(country: str = Form(..., description='Choose a country:',example='Bulgaria', enum=countries.countries),
                             sports_club: str = Form(..., description='Choose a club sport:', example='Tenis Stars', enum=sport_clubs.sport_clubs),
             x_token: str = Header()):
    ''' Used for creating and sending a request for creating a player.

    Args:
        - country: str(Query)
        - sports_club: str(Query)
        - JWT token(Header)
    
    Returns:
        - Created director request
    '''

    return user_service.create_director_request(country, sports_club, x_token)


@director_requests_router.get('/', description='View all your requests for creating a player:')
def find_all_director_requests(x_token: str = Header()):
    ''' Used to get all sent and received creation requests.
    
    Args:
        - JWT token(Header)
    
    Returns:
        - list of all user's requests
    '''

    return user_service.get_all_director_requests(x_token)


@director_requests_router.get('/id', description='View specific director request:')
def find_director_request_by_id(id: int = Query(..., description='Enter ID of the director request you want to view:'),
                      x_token: str = Header()):
    ''' Used to to get all sent and received user director requests.
    
    Args:
        - JWT token(Header)
    
    Returns:
        - Director request
    '''

    return user_service.get_director_request_by_id(id, x_token)
    

@director_requests_router.delete('/', description="Please fill the form to delete your director request:")
def delete_director_request(id: int = Query(..., description='Enter ID of the director request you want to delete:'), 
                x_token: str = Header()
                ):
    ''' Used for deleting an already created director request for creating a players if the status is 'pending'.

    Args:
        - requests.id: int(URL link)
        - JWT token
    
    Returns:
        - Deleted director request
    '''

    return user_service.delete_director_request_by_id(id, x_token)
