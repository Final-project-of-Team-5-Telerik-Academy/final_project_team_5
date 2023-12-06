import unittest
from unittest.mock import patch
from unittest import mock
from my_models.model_admin_requests import AdminRequests
from my_models.model_director_requests import DirectorRequests
from services import user_service
from hashlib import sha256


class UserServicesTests(unittest.TestCase):

    @mock.patch('hashlib.sha256', wraps=sha256)
    def test_hash_password(self, mock_sha256):
        # Arrange
        mock_sha256.return_value.hexdigest.return_value = 'hashed_password'

        # Act
        result = user_service._hash_password('password123')

        # Assert
        mock_sha256.assert_called_once_with('password123'.encode('utf-8'))
        self.assertEqual(result, 'hashed_password')

    @patch('services.user_service.insert_query')
    def test_delete_account(self, mock_insert_query):
        # Arrange
        mock_insert_query.return_value = []

        # Act
        result = user_service.delete_account(2)

        # Assert
        mock_insert_query('''DELETE FROM users WHERE id = ?''',
                 (2,))
        self.assertIsNone(result)

    @patch('services.user_service.read_query')
    def test_find_all_admin_requests(self, mock_read_query):
        # Arrange
        mock_read_query.return_value = [(1, 'connection', None, 2, 'pending')]

        # Act
        result = user_service.find_all_admin_requests(1)

        # Assert
        mock_read_query.assert_called_once_with(
            'SELECT id, type_of_request, players_id, users_id, status FROM admin_requests WHERE users_id = ?',
            (1,))
        self.assertIsNotNone(result)

    @patch('services.user_service.read_query')
    def test_find_all_user_director_requests(self, mock_read_query):

        # Arrange
        mock_read_query.return_value = [(1, 'Petar Toshev', 'Bulgaria', 'Diva', 2, 'connection',)]

        # Act
        result = user_service.find_all_user_director_requests(1)

        # Assert
        mock_read_query.assert_called_once_with(
            'SELECT id, full_name, country, sports_club, users_id, status FROM director_requests WHERE users_id = ?',
            (1,))

        self.assertIsNotNone(result)

    @patch('services.user_service.read_query')
    def test_find_all_user_director_requests_empty_result(self, mock_read_query):
        # Arrange
        mock_read_query.return_value = []

        # Act
        result_generator = user_service.find_all_user_director_requests(1)
        result_list = list(result_generator)

        # Assert
        mock_read_query(
            'SELECT id, full_name, country, sports_club, users_id, status FROM director_requests WHERE users_id = ?',
            (1,)
        )

        self.assertEqual(result_list, [])

    @patch('services.user_service.read_query')
    def test_find_admin_request_by_id_and_users_id(self, mock_read_query):
        # Arrange
        mock_read_query.return_value = [(1, 'connection', None, 3, 'pending',)]

        # Act
        result = user_service.find_admin_request_by_id_and_users_id(1, 3)

        # Assert
        mock_read_query.assert_called_once_with(
            'SELECT id, type_of_request, players_id, users_id, status FROM admin_requests WHERE id = ? and users_id = ?',
            (1, 3))

        self.assertIsInstance(result, AdminRequests)

        self.assertEqual(result.id, 1)
        self.assertEqual(result.type_of_request, 'connection')
        self.assertEqual(result.players_id, None)
        self.assertEqual(result.users_id, 3)
        self.assertEqual(result.status, 'pending')

    @patch('services.user_service.insert_query')
    def test_send_connection_request(self, mock_insert):
        # Arrange
        generated_id = 2
        mock_insert.return_value = generated_id

        # Act
        result = user_service.send_connection_request('connection', 1, 3)

        # Assert
        mock_insert.assert_called_once_with(
            'INSERT INTO admin_requests(type_of_request, players_id, users_id, status) VALUES (?,?,?,?)',
            ('connection', 1, 3, 'pending')
        )

        self.assertIsInstance(result, AdminRequests)
        self.assertEqual(result.id, generated_id)
        self.assertEqual(result.type_of_request, 'connection')
        self.assertEqual(result.players_id, 1)
        self.assertEqual(result.users_id, 3)
        self.assertEqual(result.status, 'pending')

    @patch('services.user_service.read_query')
    def test_get_user_full_name_by_id(self, mock_read_query):
        # Arrange
        mock_read_query.return_value = [('John Doe',)]

        # Act
        result = user_service.get_user_full_name_by_id(1)

        # Assert
        mock_read_query.assert_called_once_with('SELECT full_name FROM users WHERE id = ?', (1,))
        self.assertEqual(result, 'John Doe')

    @patch('services.user_service.validate_email')
    @patch('services.user_service.verify_account')
    def test_verificated_user(self, mock_verify_account, mock_validate_email):

        # Arrange
        mock_validate_email.return_value = None
        mock_verify_account.return_value = True

        # Act
        result = user_service.verificated_user('test@example.com', 'verification_code')

        # Assert
        mock_validate_email.assert_called_once_with('test@example.com', check_deliverability=False)
        mock_verify_account.assert_called_once_with('test@example.com', 'verification_code')
        self.assertTrue(result)

    @patch('services.user_service.read_query')
    def test_get_director_requests_by_id(self, mock_read_query):
        # Arrange
        mock_read_query.return_value = [(1, 'Andrey Popov', 'USA', 'Diva', 3, 'pending',)]

        # Act
        result_generator = user_service.get_director_requests_by_id(1, )

        # Assert
        mock_read_query.assert_called_once_with(
            'SELECT id, full_name, country, sports_club, users_id, status FROM director_requests WHERE id = ?',
            (1,))

        for result in result_generator:
            self.assertIsInstance(result, DirectorRequests)
            self.assertEqual(result.id, 1)
            self.assertEqual(result.full_name, 'Andrey Popov')
            self.assertEqual(result.country, 'USA')
            self.assertEqual(result.sports_club, 'Diva')
            self.assertEqual(result.users_id, 3)
            self.assertEqual(result.status, 'pending')

    @patch('services.user_service.read_query')
    def test_get_director_requests_by_id_empty_result(self, mock_read_query):
        # Arrange
        mock_read_query.return_value = []

        # Act
        result_generator = user_service.get_director_requests_by_id(1)
        result_list = list(result_generator)

        # Assert
        mock_read_query.assert_called_once_with(
            'SELECT id, full_name, country, sports_club, users_id, status FROM director_requests WHERE id = ?',
            (1,)
        )

        self.assertEqual(result_list, [])

    @patch('services.user_service.read_query')
    def test_get_director_requests_by_id_empty_answer(self, mock_read_query):
        # Arrange
        mock_read_query.return_value = []

        # Act
        result_generator = user_service.get_director_requests_by_id(1)

        # Assert
        mock_read_query.assert_called_once_with(
            'SELECT id, full_name, country, sports_club, users_id, status FROM director_requests WHERE id = ?',
            (1,)
        )

        self.assertFalse(any(result_generator), "Result should be an empty generator")

    @patch('services.user_service.read_query')
    def test_find_director_request_by_id_and_users_id(self, mock_read_query):
        # Arrange
        mock_read_query.return_value = [(1, 'Andrey Popov', 'USA', 'Diva', 2, 'pending',)]

        # Act
        result = user_service.find_director_request_by_id_and_users_id(1, 2)

        # Assert
        mock_read_query.assert_called_once_with(
            'SELECT id, full_name, country, sports_club, users_id, status FROM director_requests WHERE id = ? and users_id = ?',
            (1, 2))

        self.assertIsInstance(result, DirectorRequests)

        self.assertEqual(result.id, 1)
        self.assertEqual(result.full_name, 'Andrey Popov')
        self.assertEqual(result.country, 'USA')
        self.assertEqual(result.sports_club, 'Diva')
        self.assertEqual(result.users_id, 2)
        self.assertEqual(result.status, 'pending')

    @patch('services.user_service.read_query')
    def test_find_all_director_requests(self, mock_read_query):
        # Arrange
        mock_read_query.return_value = [(1, 'Andrey Popov', 'USA', 'Diva', 3, 'pending',)]

        # Act
        result_generator = user_service.find_all_director_requests()

        # Assert
        mock_read_query(
            'SELECT id, full_name, country, sports_club, users_id, status FROM director_requests',
            ())

        for result in result_generator:
            self.assertIsInstance(result, DirectorRequests)
            self.assertEqual(result.id, 1)
            self.assertEqual(result.full_name, 'Andrey Popov')
            self.assertEqual(result.country, 'USA')
            self.assertEqual(result.sports_club, 'Diva')
            self.assertEqual(result.users_id, 3)
            self.assertEqual(result.status, 'pending')

    @patch('services.user_service.read_query')
    def test_find_all_director_requests_empty_result(self, mock_read_query):
        # Arrange
        mock_read_query.return_value = []

        # Act
        result_generator = user_service.find_all_director_requests()

        # Assert
        mock_read_query(
            'SELECT id, full_name, country, sports_club, users_id, status FROM director_requests',
            ())

        # Convert the generator to a list to check its emptiness
        result_list = list(result_generator)

        # Assert that the result list is empty
        self.assertEqual(result_list, [])

    @patch('services.user_service.read_query')
    def test_find_all_director_requests_empty_answer(self, mock_read_query):
        # Arrange
        mock_read_query.return_value = []

        # Act
        result_generator = user_service.find_all_director_requests()

        # Assert
        mock_read_query(
            'SELECT id, full_name, country, sports_club, users_id, status FROM director_requests', ())

        result_list = list(result_generator)

        self.assertEqual(result_list, [])

    @patch('services.user_service.read_query')
    def test_director_request_does_not_exist(self, mock_read_query):

        # Arrange
        mock_read_query.return_value = []

        # Act
        result = user_service.director_request_exists('Alek Martinson', )

        # Assert
        mock_read_query.assert_called_once_with(
            'SELECT id, full_name, country, sports_club, users_id, status FROM director_requests WHERE full_name = ? '
            'and status = ?', ('Alek Martinson', 'pending')
        )
        self.assertFalse(result)

    @patch('services.user_service.update_query')
    def test_update_director_request_status(self, mock_update_query):
        # Arrange
        mock_update_query.return_value = []

        # Act
        result = user_service.update_director_request_status('connection', 'Martin Garett', 'pending')

        # Assert
        mock_update_query.assert_called_once_with(
            'UPDATE director_requests SET status = ? WHERE full_name = ? and status = ?',
            ('connection', 'Martin Garett', 'pending')
        )
        self.assertEqual(result, None)

    @patch('services.user_service.read_query')
    def test_players_id_exists_in_users(self, mock_read_query):

        # Arrange
        mock_read_query.return_value = [
            (3, 'Bob Ross', 'bob_ross@gmail.com', '******', 'male', 'player', 4, '******', '******')]

        # Act
        result = user_service.players_id_exists_in_users(4, 'Bob Ross')

        # Assert
        mock_read_query.assert_called_once_with(
            'SELECT id, full_name, email, password, gender, role, players_id, is_verified, verification_code FROM users WHERE players_id = ? and full_name = ?',
            (4, 'Bob Ross'))
        self.assertTrue(result)


if __name__ == '__main__':
    unittest.main()