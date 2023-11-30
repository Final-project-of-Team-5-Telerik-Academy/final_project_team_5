import unittest
from unittest.mock import patch
from authentication import authenticator


class AuthenticatorsTests(unittest.TestCase):


    @patch('authentication.authenticator.read_query')
    def test_find_by_email(self, mock_read_query):

        # Arrange
        mock_read_query.return_value = [(7, 'Frank Warren', 'warwarbinks@gmail.com', '74fca0325b5fdb3a34badb40a2581cfbd5344187e8d3432952a5abc0929c1246', 'male', 'player', 4, 1, 123456)]

        # Act
        result = authenticator.find_by_email('warwarbinks@gmail.com')

        # Assert
        mock_read_query.assert_called_once_with(
        'SELECT id, full_name, email, password, gender, role, players_id, is_verified, verification_code FROM users WHERE email = ?',
        ('warwarbinks@gmail.com',))
        self.assertTrue(result)


    @patch('authentication.authenticator.read_query')
    def test_find_by_id(self, mock_read_query):

        # Arrange
        mock_read_query.return_value = [(7, 'Frank Warren', 'warwarbinks@gmail.com', '74fca0325b5fdb3a34badb40a2581cfbd5344187e8d3432952a5abc0929c1246', 'male', 'player', 4, 1, 123456)]

        # Act
        result = authenticator.find_by_id(7)

        # Assert
        mock_read_query.assert_called_once_with(
        'SELECT id, full_name, email, password, gender, role, players_id, is_verified, verification_code FROM users WHERE id = ?',
        (7,))
        self.assertTrue(result)


if __name__ == '__main__':
    unittest.main()