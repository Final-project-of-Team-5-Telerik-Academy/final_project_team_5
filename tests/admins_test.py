import unittest
from unittest.mock import patch, Mock, call
from my_models.model_user import User
from services import admin_service
from fastapi.responses import JSONResponse


class AdminsTests(unittest.TestCase):


    @patch('services.admin_service.read_query')
    def test_find_all_users(self, mock_read_query):

        # Arrange
        mock_read_query.return_value = [(3, 'Bob Ross', 'bob_ross@gmail.com', '******', 'male', 'spectator', None, '******', '******'), (4, 'Van Gross', 'van_Gross@gmail.com', '******', 'male', 'spectator', None, '******', '******')]

        # Act
        result = admin_service.find_all_users()

        # Assert
        mock_read_query.assert_called_once_with(
            'SELECT id, full_name, email, password, gender, role, players_id, is_verified, verification_code FROM users',
        )
        self.assertTrue(result)


    @patch('services.admin_service.read_query')
    def test_do_not_find_all_users(self, mock_read_query):

        # Arrange
        mock_read_query.return_value = None

        # Act
        result = admin_service.find_all_users()

        # Assert
        mock_read_query.assert_called_once_with(
            'SELECT id, full_name, email, password, gender, role, players_id, is_verified, verification_code FROM users',
        )
        expected_response = JSONResponse(status_code=404, content='There are no registered users.')
        self.assertEqual(result.status_code, expected_response.status_code)
        self.assertEqual(result.body, expected_response.body)


    @patch('services.admin_service.read_query')
    def test_find_user_by_role(self, mock_read_query):

        # Arrange
        mock_read_query.return_value = [(3, 'Bob Ross', 'bob_ross@gmail.com', '******', 'male', 'spectator', None, '******', '******'), (4, 'Van Gross', 'van_Gross@gmail.com', '******', 'male', 'spectator', None, '******', '******')]

        # Act
        result = admin_service.find_user_by_role('spectator')

        # Assert
        mock_read_query.assert_called_once_with('SELECT id, full_name, email, password, gender, role, players_id, is_verified, verification_code FROM users WHERE role = ?',
                      ('spectator',))
        
        self.assertTrue(result)


    @patch('services.admin_service.read_query')
    def test_do_not_find_user_by_role(self, mock_read_query):

        # Arrange
        mock_read_query.return_value = None

        # Act
        result = admin_service.find_user_by_role('spectator')

        # Assert
        mock_read_query.assert_called_once_with('SELECT id, full_name, email, password, gender, role, players_id, is_verified, verification_code FROM users WHERE role = ?',
                      ('spectator',))
        
        expected_response = JSONResponse(status_code=404, content='There are no users with that role.')
        self.assertEqual(result.status_code, expected_response.status_code)
        self.assertEqual(result.body, expected_response.body)


    @patch('services.admin_service.read_query')
    def test_find_user_by_id(self, mock_read_query):

        # Arrange
        mock_read_query.return_value = [(3, 'Bob Ross', 'bob_ross@gmail.com', '******', 'male', 'spectator', None, '******', '******')]

        # Act
        result = admin_service.find_user_by_id(3)

        # Assert
        mock_read_query.assert_called_once_with(
        'SELECT id, full_name, email, password, gender, role, players_id, is_verified, verification_code FROM users WHERE id = ?',
        (3,)
        )
        
        self.assertTrue(result)


    @patch('services.admin_service.read_query')
    def test_do_not_find_user_by_id(self, mock_read_query):

        # Arrange
        mock_read_query.return_value = None

        # Act
        result = admin_service.find_user_by_id(3)

        # Assert
        mock_read_query.assert_called_once_with(
        'SELECT id, full_name, email, password, gender, role, players_id, is_verified, verification_code FROM users WHERE id = ?',
        (3,)
        )
        
        expected_response = JSONResponse(status_code=404, content='User with ID: 3 does not exist.')
        self.assertEqual(result.status_code, expected_response.status_code)
        self.assertEqual(result.body, expected_response.body)


    @patch('services.admin_service.update_query')
    def test_edit_user_role(self, mock_update_query):

        # Arrange
        edited_user = User(
        id=3,
        full_name='Bob Ross',
        email='bob_ross@gmail.com',
        password='ef797c8118f02dfb649607dd5d3f8c7623048c9c063d532cc95c5ed7a898a64f',
        gender='male',
        role='spectator',
        players_id=None,
        is_verified='1',
        verification_code='123456'
    )
        mock_update_query.return_value = "User's role is updated."

        # Act
        result = admin_service.edit_user_role(edited_user, 'player')

        # Assert
        mock_update_query.assert_called_once_with('''UPDATE users SET role = ? WHERE id = ?''', ('player', 3))
        self.assertTrue(result)


    @patch('services.admin_service.update_query')
    def test_edit_user_players_id(self, mock_update_query):

        # Arrange
        edited_user = User(
        id=3,
        full_name='Bob Ross',
        email='bob_ross@gmail.com',
        password='ef797c8118f02dfb649607dd5d3f8c7623048c9c063d532cc95c5ed7a898a64f',
        gender='male',
        role='spectator',
        players_id=None,
        is_verified='1',
        verification_code='123456'
    )
        mock_update_query.return_value = 'User is successfully connectected to player.'

        # Act
        result = admin_service.edit_user_players_id(edited_user, 4)

        # Assert
        mock_update_query.assert_called_once_with('''UPDATE users SET players_id = ? WHERE id = ?''', (4, 3))
        self.assertTrue(result)


    @patch('services.admin_service.insert_query')
    def test_delete_user(self, mock_insert_query):

        # Arrange
        mock_insert_query.return_value = None

        # Act
        result = admin_service.delete_user(2)

        # Assert
        mock_insert_query.assert_called_once_with('''DELETE FROM users WHERE id = ?''',
                 (2,))
        self.assertIsNone(result)


    @patch('services.admin_service.update_query')
    def test_delete_players_id_from_user(self, mock_update_query):

        # Arrange
        mock_update_query.return_value = None

        # Act
        result = admin_service.delete_players_id_from_user(2)

        # Assert
        mock_update_query.assert_called_once_with('''UPDATE users SET players_id = NULL WHERE id = ?''',
                 (2,))
        self.assertIsNone(result)


    @patch('services.admin_service.read_query')
    def test_get_all_admin_requests(self, mock_read_query):

        # Arrange
        mock_read_query.return_value = [(1, 'connection', 3, 2, 'pending'), (2, 'promotion', None, 3, 'pending')]

        # Act
        result = admin_service.get_all_admin_requests()

        # Assert
        mock_read_query.assert_called_once_with('SELECT id, type_of_request, players_id, users_id, status FROM admin_requests')       
        self.assertTrue(result)


    @patch('services.admin_service.read_query')
    def test_do_not_get_all_admin_requests(self, mock_read_query):

        # Arrange
        mock_read_query.return_value = None

        # Act
        result = admin_service.get_all_admin_requests()

        # Assert
        mock_read_query.assert_called_once_with('SELECT id, type_of_request, players_id, users_id, status FROM admin_requests')
        expected_response = JSONResponse(status_code=404, content='There are no requests')
        self.assertEqual(result.status_code, expected_response.status_code)
        self.assertEqual(result.body, expected_response.body)


    @patch('services.admin_service.read_query')
    def test_get_admin_request_by_id(self, mock_read_query):

        # Arrange
        mock_read_query.return_value = [(1, 'connection', 3, 2, 'pending')]

        # Act
        result = admin_service.get_admin_request_by_id(1)

        # Assert
        mock_read_query.assert_called_once_with('SELECT id, type_of_request, players_id, users_id, status FROM admin_requests WHERE id = ?',
                      (1,))
        self.assertTrue(result)


    @patch('services.admin_service.read_query')
    def test_do_not_get_admin_request_by_id(self, mock_read_query):

        # Arrange
        mock_read_query.return_value = None

        # Act
        result = admin_service.get_admin_request_by_id(1)

        # Assert
        mock_read_query.assert_called_once_with('SELECT id, type_of_request, players_id, users_id, status FROM admin_requests WHERE id = ?',
                      (1,))
        expected_response = JSONResponse(status_code=404, content='Admin request with ID: 1 does not exist.')
        self.assertEqual(result.status_code, expected_response.status_code)
        self.assertEqual(result.body, expected_response.body)


    @patch('services.admin_service.update_query')
    def test_edit_requests_connection_status(self, mock_update_query):

        # Arrange
        mock_update_query.return_value = None

        # Act
        result = admin_service.edit_requests_connection_status('finished', 3, 'connection', 2)

        # Assert
        mock_update_query.assert_called_once_with('''UPDATE admin_requests SET status = ? WHERE players_id = ? and type_of_request = ? and users_id = ?''',
                ('finished', 3, 'connection', 2))
        self.assertIsNone(result)


    @patch('services.admin_service.update_query')
    def test_edit_requests_promotion_status(self, mock_update_query):

        # Arrange
        mock_update_query.return_value = None

        # Act
        result = admin_service.edit_requests_promotion_status('finished', 'promotion', 2)

        # Assert
        mock_update_query.assert_called_once_with('''UPDATE admin_requests SET status = ? WHERE type_of_request = ? and users_id = ?''',
                ('finished', 'promotion', 2))
        self.assertIsNone(result)


    @patch('services.admin_service.insert_query')
    def test_insert_banned_player(self, mock_insert_query):

        # Arrange
        mock_insert_query.return_value = 2

        # Act
        result = admin_service.insert_banned_player(2, 'permanent')

        # Assert
        mock_insert_query.assert_called_once_with(
        'INSERT INTO banned_players(players_id, ban_status) VALUES (?, ?)',
        (2, 'permanent'))
        self.assertTrue(result)


    @patch('services.admin_service.read_query')
    def test_get_all_banned_players(self, mock_read_query):

        # Arrange
        mock_read_query.return_value = [(1, 3, 'permanent'), (2, 4, 'temporary')]

        # Act
        result = admin_service.get_all_banned_players()

        # Assert
        mock_read_query.assert_called_once_with('SELECT id, players_id, ban_status FROM banned_players')
        self.assertTrue(result)


    @patch('services.admin_service.read_query')
    def test_do_not_get_all_banned_players(self, mock_read_query):

        # Arrange
        mock_read_query.return_value = None

        # Act
        result = admin_service.get_all_banned_players()

        # Assert
        mock_read_query.assert_called_once_with('SELECT id, players_id, ban_status FROM banned_players')
        expected_response = JSONResponse(status_code=404, content='There are no banned players.')
        self.assertEqual(result.status_code, expected_response.status_code)
        self.assertEqual(result.body, expected_response.body)


    @patch('services.admin_service.insert_query')
    def test_remove_banned_player(self, mock_insert_query):

        # Arrange
        mock_insert_query.return_value = None

        # Act
        result = admin_service.remove_banned_player(2)

        # Assert
        mock_insert_query.assert_called_once_with('''DELETE FROM banned_players WHERE players_id = ?''',
                 (2,))
        self.assertIsNone(result)


if __name__ == '__main__':
    unittest.main()