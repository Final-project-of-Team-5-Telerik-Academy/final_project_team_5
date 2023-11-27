from fastapi import APIRouter, Header, Query, Form
from services import user_service


admin_requests_router = APIRouter(prefix='/admin_requests', tags={'Admin Requests'})


@admin_requests_router.post('/', description="Please fill the form to create and send a connection/promotion request:")
def create_admin_request(type_of_request: str = Form(..., description='Choose your role:',example='connection', enum = ['connection', 'promotion']),
             players_id: int = Query(default=None, description="Enter ID of the player's account:"),
             x_token: str = Header()):
    ''' Used for creating and sending a request for connection or promotion.

    Args:
        - type_of_request: str(Query)
        - players_id: int(Query)
        - JWT token(Header)
    
    Returns:
        - Created admin request
    '''

    return user_service.create_and_send_admin_request(type_of_request, players_id, x_token)


@admin_requests_router.get('/', description='View all your requests:')
def find_all_admin_requests(x_token: str = Header()):
    ''' Used to get all sent and received user requests.
    
    Args:
        - JWT token(Header)
    
    Returns:
        - list of all user's requests
    '''

    return user_service.get_all_admin_requests(x_token)


@admin_requests_router.get('/id', description='View specific request:')
def find_admin_request_by_id(id: int = Query(..., description='Enter ID of the request you want to view:'),
                      x_token: str = Header()):
    ''' Used to to get a sent and received user request by id.
    
    Args:
        - JWT token(Header)
    
    Returns:
        - user's request
    '''

    return user_service.get_admin_request_by_id(id, x_token)
    

@admin_requests_router.delete('/', description="Please fill the form to delete your request:")
def delete_admin_request(id: int = Query(..., description='Enter ID of the request you want to delete:'), 
                x_token: str = Header()):
    ''' Used for deleting an already created request for connection or promotion if the status is 'pending'.

    Args:
        - requests.id: int(URL link)
        - JWT token
    
    Returns:
        - Deleted request
    '''

    return user_service.delete_admin_request_by_id(id, x_token)
