import unittest
from unittest.mock import patch, Mock

import services.shared_service
from services import shared_service
from services.shared_service import id_exists
from my_models.model_admin_requests import AdminRequests
from my_models.model_director_requests import DirectorRequests

class AdminRequestsTests(unittest.TestCase):

    @patch('services.shared_service.read_query')
    def test_id_exists_bool(self, mock_read_query):

        # Arrange
        mock_read_query.return_value = [(1,)]

        # Act
        result = shared_service.id_exists(1, 'admin_requests')

        # Assert
        mock_read_query.assert_called_once_with(
            'SELECT id FROM admin_requests WHERE id = ?',
            (1,)
        )
        self.assertTrue(result)

    @patch('services.shared_service.read_query')
    def test_id_does_not_exist_bool(self, mock_read_query):

        # Arrange
        mock_read_query.return_value = []

        # Act
        result = shared_service.id_exists(1, 'admin_requests')

        # Assert
        mock_read_query.assert_called_once_with(
            'SELECT id FROM admin_requests WHERE id = ?',
            (1,)
        )
        self.assertFalse(result)

    @patch('services.shared_service.read_query')
    def test_admin_request_by_id_exists_promotion(self, mock_read_query):

        # Arrange
        mock_read_query.return_value = [(1, 'promotion', None, 2, 'pending')]

        # Act
        result = shared_service.id_exists_admin_requests(1)

        # Assert
        mock_read_query.assert_called_once_with(
            'SELECT id, type_of_request, players_id, users_id, status FROM admin_requests WHERE id = ?',
            (1,))

        self.assertIsInstance(result, AdminRequests)

        self.assertEqual(result.id, 1)
        self.assertEqual(result.type_of_request, 'promotion')
        self.assertEqual(result.players_id, None)
        self.assertEqual(result.users_id, 2)
        self.assertEqual(result.status, 'pending')

    @patch('services.shared_service.read_query')
    def test_admin_request_by_id_does_not_exist_promotion(self, mock_read_query):
        # Arrange
        mock_read_query.return_value = []

        # Act
        result = shared_service.id_exists_admin_requests(2)

        # Assert
        mock_read_query.assert_called_once_with(
            'SELECT id, type_of_request, players_id, users_id, status FROM admin_requests WHERE id = ?',
            (2,))
        self.assertIsNone(result)

    @patch('services.shared_service.read_query')
    def test_admin_request_by_id_exists_connection(self, mock_read_query):

        # Arrange
        mock_read_query.return_value = [(1, 'connection', 1, 2, 'pending')]

        # Act
        result = shared_service.id_exists_admin_requests(1)

        # Assert
        mock_read_query.assert_called_once_with(
            'SELECT id, type_of_request, players_id, users_id, status FROM admin_requests WHERE id = ?',
            (1,))
        self.assertIsInstance(result, AdminRequests)

        self.assertEqual(result.id, 1)
        self.assertEqual(result.type_of_request, 'connection')
        self.assertEqual(result.players_id, 1)
        self.assertEqual(result.users_id, 2)
        self.assertEqual(result.status, 'pending')

    @patch('services.shared_service.read_query')
    def test_admin_request_by_id_does_not_exist_connection(self, mock_read_query):

        # Arrange
        mock_read_query.return_value = []

        # Act
        result = shared_service.id_exists_admin_requests(2)

        # Assert
        mock_read_query.assert_called_once_with(
            'SELECT id, type_of_request, players_id, users_id, status FROM admin_requests WHERE id = ?',
            (2,))
        self.assertIsNone(result)

    @patch('services.shared_service.read_query')
    def test_id_exists_admin_requests_full_info_promotion(self, mock_read_query):

        # Arrange
        mock_read_query.return_value = [(1, 'promotion', None, 2, 'pending')]

        # Act
        result = shared_service.id_exists_admin_requests_full_info(1)

        # Assert
        mock_read_query.assert_called_once_with(
            'SELECT id, type_of_request, players_id, users_id, status FROM admin_requests WHERE id = ?',
            (1,))
        self.assertIsInstance(result, AdminRequests)

        self.assertEqual(result.id, 1)
        self.assertEqual(result.type_of_request, 'promotion')
        self.assertEqual(result.players_id, None)
        self.assertEqual(result.users_id, 2)
        self.assertEqual(result.status, 'pending')

    @patch('services.shared_service.read_query')
    def test_id_does_not_exists_admin_requests_full_info_promotion(self, mock_read_query):

        # Arrange
        mock_read_query.return_value = []

        # Act
        result = shared_service.id_exists_admin_requests_full_info(2)

        # Assert
        mock_read_query.assert_called_once_with(
            'SELECT id, type_of_request, players_id, users_id, status FROM admin_requests WHERE id = ?',
            (2,))
        self.assertIsNone(result)

    @patch('services.shared_service.read_query')
    def test_id_exists_director_requests(self, mock_read_query):

        # Arrange
        mock_read_query.return_value = [(1, 'Petar Georgiev', 'USA', 'Diva', 2, 'pending')]

        # Act
        result = shared_service.id_exists_director_requests(1)

        # Assert
        mock_read_query.assert_called_once_with(
            'SELECT id, full_name, country, sports_club, users_id, status FROM director_requests WHERE id = ?',
            (1,))
        self.assertIsInstance(result, DirectorRequests)

        self.assertEqual(result.id, 1)
        self.assertEqual(result.full_name, 'Petar Georgiev')
        self.assertEqual(result.country, 'USA')
        self.assertEqual(result.sports_club, 'Diva')
        self.assertEqual(result.users_id, 2)
        self.assertEqual(result.status, 'pending')

    @patch('services.shared_service.read_query')
    def test_id_does_not_exist_director_requests(self, mock_read_query):

        # Arrange
        mock_read_query.return_value = []

        # Act
        result = shared_service.id_exists_director_requests(2)

        # Assert
        mock_read_query.assert_called_once_with(
            'SELECT id, full_name, country, sports_club, users_id, status FROM director_requests WHERE id = ?',
            (2,))
        self.assertIsNone(result)

    @patch('services.shared_service.read_query')
    def test_user_connection_request_exists(self, mock_read_query):

        # Arrange
        mock_read_query.return_value = [(1, 'connection', 1, 2, 'pending')]

        # Act
        result = shared_service.user_connection_request_exists(1)

        # Assert
        mock_read_query.assert_called_once_with(
            'SELECT id, type_of_request, players_id, users_id, status FROM admin_requests WHERE users_id = ? and status = ? and type_of_request = ?',
            (1, 'pending', 'connection')
        )
        self.assertIsInstance(result, AdminRequests)

        self.assertEqual(result.id, 1)
        self.assertEqual(result.type_of_request, 'connection')
        self.assertEqual(result.players_id, 1)
        self.assertEqual(result.users_id, 2)
        self.assertEqual(result.status, 'pending')

    @patch('services.shared_service.read_query')
    def test_user_connection_request_does_not_exist(self, mock_read_query):
        # Arrange
        mock_read_query.return_value = []

        # Act
        result = shared_service.user_connection_request_exists(1)

        # Assert
        mock_read_query.assert_called_once_with(
            'SELECT id, type_of_request, players_id, users_id, status FROM admin_requests WHERE users_id = ? and status = ? and type_of_request = ?',
            (1, 'pending', 'connection')
        )
        self.assertIsNone(result)


    @patch('services.shared_service.read_query')
    def test_user_promotion_request_exists(self, mock_read_query):
        # Arrange
        mock_read_query.return_value = [(1, 'promotion', None, 2, 'pending')]

        # Act
        result = shared_service.user_promotion_request_exists(1)

        # Assert
        mock_read_query.assert_called_once_with(
            'SELECT id, type_of_request, players_id, users_id, status FROM admin_requests WHERE users_id = ? and status = ? and type_of_request = ?',
            (1, 'pending', 'promotion')
        )
        self.assertIsInstance(result, AdminRequests)

        self.assertEqual(result.id, 1)
        self.assertEqual(result.type_of_request, 'promotion')
        self.assertEqual(result.players_id, None)
        self.assertEqual(result.users_id, 2)
        self.assertEqual(result.status, 'pending')

    @patch('services.shared_service.read_query')
    def test_user_promotion_request_does_not_exist(self, mock_read_query):
        # Arrange
        mock_read_query.return_value = []

        # Act
        result = shared_service.user_promotion_request_exists(1)

        # Assert
        mock_read_query.assert_called_once_with(
            'SELECT id, type_of_request, players_id, users_id, status FROM admin_requests WHERE users_id = ? and status = ? and type_of_request = ?',
            (1, 'pending', 'promotion')
        )
        self.assertIsNone(result)

    @patch('services.shared_service.read_query')
    def test_director_request_exists(self, mock_read_query):
        # Arrange
        mock_read_query.return_value = [(1, 'Alexander Hristov', 'USA', 'Diva', 2, 'pending')]

        # Act
        result = shared_service.director_request_exists(1)

        # Assert
        mock_read_query.assert_called_once_with(
            'SELECT id, full_name, country, sports_club, users_id, status FROM director_requests WHERE users_id = ? and status = ?',
            (1, 'pending')
        )
        self.assertIsInstance(result, DirectorRequests)

        self.assertEqual(result.id, 1)
        self.assertEqual(result.full_name, 'Alexander Hristov')
        self.assertEqual(result.country, 'USA')
        self.assertEqual(result.sports_club, 'Diva')
        self.assertEqual(result.users_id, 2)
        self.assertEqual(result.status, 'pending')

    @patch('services.shared_service.read_query')
    def test_director_request_does_not_exist(self, mock_read_query):
        # Arrange
        mock_read_query.return_value = []

        # Act
        result = shared_service.director_request_exists(1)

        # Assert
        mock_read_query.assert_called_once_with(
            'SELECT id, full_name, country, sports_club, users_id, status FROM director_requests WHERE users_id = ? and status = ?',
            (1, 'pending')
        )
        self.assertIsNone(result)

    @patch('services.shared_service.read_query')
    def test_players_id_exists(self, mock_read_query):
        # Arrange
        mock_read_query.return_value = [(1,)]

        # Act
        result = shared_service.players_id_exists(1, 'admin_requests')

        # Assert
        mock_read_query.assert_called_once_with(
            'SELECT players_id FROM admin_requests WHERE players_id = ?',
            (1,)
        )
        self.assertTrue(result)

    @patch('services.shared_service.read_query')
    def test_players_id_does_not_exist(self, mock_read_query):
        # Arrange
        mock_read_query.return_value = []

        # Act
        result = shared_service.players_id_exists(1, 'admin_requests')

        # Assert
        mock_read_query.assert_called_once_with(
            'SELECT players_id FROM admin_requests WHERE players_id = ?',
            (1,)
        )
        self.assertFalse(result)

    @patch('services.shared_service.read_query')
    def test_email_exists(self, mock_read_query):
        # Arrange
        mock_read_query.return_value = [('petar@gmail.com',)]

        # Act
        result = shared_service.email_exists('petar@gmail.com')

        # Assert
        mock_read_query.assert_called_once_with(
            'SELECT email FROM users WHERE email = ?',
            ('petar@gmail.com',)
        )
        self.assertTrue(result)

    @patch('services.shared_service.read_query')
    def test_email_does_not_exist(self, mock_read_query):
        # Arrange
        mock_read_query.return_value = []

        # Act
        result = shared_service.email_exists('petar@gmail.com')

        # Assert
        mock_read_query.assert_called_once_with(
            'SELECT email FROM users WHERE email = ?',
            ('petar@gmail.com',)
        )
        self.assertFalse(result)

    @patch('services.shared_service.read_query')
    def test_full_name_exists(self, mock_read_query):
        # Arrange
        mock_read_query.return_value = [('Alexander Hristov',)]

        # Act
        result = shared_service.full_name_exists('Alexander Hristov','users')

        # Assert
        mock_read_query.assert_called_once_with(
            'SELECT full_name FROM users WHERE full_name = ?',
            ('Alexander Hristov',)
        )
        self.assertTrue(result)

    @patch('services.shared_service.read_query')
    def test_full_name_does_not_exist(self, mock_read_query):
        # Arrange
        mock_read_query.return_value = []

        # Act
        result = shared_service.full_name_exists('Alexander Hristov', 'users')

        # Assert
        mock_read_query.assert_called_once_with(
            'SELECT full_name FROM users WHERE full_name = ?',
            ('Alexander Hristov',)
        )
        self.assertFalse(result)

    @patch('services.shared_service.insert_query')
    def test_delete_admin_request(self, mock_insert_query):

        # Arrange
        mock_insert_query.return_value = []

        # Act
        result = shared_service.delete_admin_request(2)

        # Assert
        mock_insert_query.assert_called_once_with(
            'DELETE FROM admin_requests WHERE id = ?',
                 (2,))
        self.assertIsNone(result)

    @patch('services.shared_service.insert_query')
    def test_delete_director_request(self, mock_insert_query):
        # Arrange
        mock_insert_query.return_value = []

        # Act
        result = shared_service.delete_director_request(2)

        # Assert
        mock_insert_query.assert_called_once_with(
            'DELETE FROM director_requests WHERE id = ?',
            (2,))
        self.assertIsNone(result)

    @patch('services.shared_service.read_query')
    def test_get_creator_full_name(self, mock_read_query):

        # Arrange
        mock_read_query.return_value = [(1,)]

        # Act
        result = shared_service.get_creator_full_name('tournaments', 'Second')

        # Assert
        mock_read_query.assert_called_once_with(
            'SELECT users_creator_id FROM tournaments WHERE title = ?',
            ('Second',)
        )
        self.assertTrue(result)

    @patch('services.shared_service.read_query')
    def test_do_not_get_creator_full_name(self, mock_read_query):
        # Arrange
        mock_read_query.return_value = []

        # Act
        result = shared_service.get_creator_full_name('tournaments', 'Second')

        # Assert
        mock_read_query.assert_called_once_with(
            'SELECT users_creator_id FROM tournaments WHERE title = ?',
            ('Second',)
        )
        self.assertFalse(result)

    @patch('services.shared_service.read_query')
    def test_id_of_player_exists(self, mock_read_query):
        # Arrange
        mock_read_query.return_value = [(1,)]

        # Act
        result = shared_service.id_of_player_exists(1)

        # Assert
        mock_read_query.assert_called_once_with(
            'SELECT id FROM players WHERE id = ?',
            (1,)
        )
        self.assertTrue(result)

    @patch('services.shared_service.read_query')
    def test_id_of_player_does_not_exist(self, mock_read_query):
        # Arrange
        mock_read_query.return_value = []

        # Act
        result = shared_service.id_of_player_exists(1)

        # Assert
        mock_read_query.assert_called_once_with(
            'SELECT id FROM players WHERE id = ?',
            (1,)
        )
        self.assertFalse(result)

    @patch('services.shared_service.read_query')
    def test_id_of_blocked_player_exists(self, mock_read_query):
        # Arrange
        mock_read_query.return_value = [(1,)]

        # Act
        result = shared_service.id_of_blocked_player_exists(1)

        # Assert
        mock_read_query.assert_called_once_with(
            'SELECT id FROM blocked_players WHERE players_id = ?',
            (1,)
        )
        self.assertTrue(result)

    @patch('services.shared_service.read_query')
    def test_id_of_blocked_player_does_not_exist(self, mock_read_query):
        # Arrange
        mock_read_query.return_value = []

        # Act
        result = shared_service.id_of_blocked_player_exists(1)

        # Assert
        mock_read_query.assert_called_once_with(
            'SELECT id FROM blocked_players WHERE players_id = ?',
            (1,)
        )
        self.assertFalse(result)


if __name__ == '__main__':
    unittest.main()
