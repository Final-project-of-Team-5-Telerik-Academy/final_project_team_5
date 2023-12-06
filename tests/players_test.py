import unittest
from unittest.mock import patch, Mock, call
from my_models.model_player import Player
from services import player_service
from fastapi.responses import JSONResponse


class PlayersTests(unittest.TestCase):


    @patch('services.player_service.read_query')
    def test_get_player_by_id(self, mock_read_query):

        # Arrange
        mock_read_query.return_value = [(3, 'Bob Ross', 'USA', 'DIVA', 0, 0, None, None)]

        # Act
        result = player_service.get_player_by_id(3)

        # Assert
        mock_read_query.assert_called_once_with(
        'SELECT id, full_name, country, sports_club, is_active, is_connected, teams_id, blocked_players_id FROM players WHERE id = ?',
        (3,)
        )
        self.assertTrue(result)


    @patch('services.player_service.read_query')
    def test_do_not_get_player_by_id(self, mock_read_query):

        # Arrange
        mock_read_query.return_value = None

        # Act
        result = player_service.get_player_by_id(3)

        # Assert
        mock_read_query.assert_called_once_with(
        'SELECT id, full_name, country, sports_club, is_active, is_connected, teams_id, blocked_players_id FROM players WHERE id = ?',
        (3,)
        )
        expected_response = JSONResponse(status_code=404, content='Player with ID: 3 does not exist.')
        self.assertEqual(result.status_code, expected_response.status_code)
        self.assertEqual(result.body, expected_response.body)


    @patch('services.player_service.read_query')
    def test_get_player_by_full_name(self, mock_read_query):

        # Arrange
        mock_read_query.return_value = [(3, 'Bob Ross', 'USA', 'DIVA', 0, 0, None, None)]

        # Act
        result = player_service.get_player_by_full_name('Bob Ross')

        # Assert
        mock_read_query.assert_called_once_with(
        'SELECT id, full_name, country, sports_club, is_active, is_connected, teams_id, blocked_players_id FROM players WHERE full_name = ?',
        ('Bob Ross',)
        )
        self.assertTrue(result)


    @patch('services.player_service.read_query')
    def test_do_not_get_player_by_full_name(self, mock_read_query):

        # Arrange
        mock_read_query.return_value = None

        # Act
        result = player_service.get_player_by_full_name('Bob Ross')

        # Assert
        mock_read_query.assert_called_once_with(
        'SELECT id, full_name, country, sports_club, is_active, is_connected, teams_id, blocked_players_id FROM players WHERE full_name = ?',
        ('Bob Ross',)
        )
        expected_response = JSONResponse(status_code=404, content='Player with full name: Bob Ross does not exist.')
        self.assertEqual(result.status_code, expected_response.status_code)
        self.assertEqual(result.body, expected_response.body)


    @patch('services.player_service.read_query')
    def test_get_all_players(self, mock_read_query):

        # Arrange
        mock_read_query.return_value = [(3, 'Bob Ross', 'USA', 'DIVA', 0, 0, None, None), (4, 'John Strong', 'Canada', 'Firefighters', 0, 0, None, None)]

        # Act
        result = player_service.get_all_players()

        # Assert
        mock_read_query.assert_called_once_with('SELECT id, full_name, country, sports_club, is_active, is_connected, teams_id, blocked_players_id FROM players')
        self.assertTrue(result)


    @patch('services.player_service.read_query')
    def test_do_not_get_all_players(self, mock_read_query):

        # Arrange
        mock_read_query.return_value = None

        # Act
        result = player_service.get_all_players()

        # Assert
        mock_read_query.assert_called_once_with('SELECT id, full_name, country, sports_club, is_active, is_connected, teams_id, blocked_players_id FROM players')
        expected_response = JSONResponse(status_code=404, content='There are no registered players.')
        self.assertEqual(result.status_code, expected_response.status_code)
        self.assertEqual(result.body, expected_response.body)


    @patch('services.player_service.insert_query')
    def test_create_player(self, mock_insert_query):

        # Arrange
        mock_insert_query.return_value = 2

        # Act
        result = player_service.create_player('Bob Ross', 'USA', 'DIVA')

        # Assert
        mock_insert_query.assert_called_once_with(
        'INSERT INTO players(full_name, country, sports_club, is_active, is_connected, teams_id, blocked_players_id) VALUES (?,?,?,?,?,?,?)',
        ('Bob Ross', 'USA', 'DIVA', 0, 0, None, None)
    )
        self.assertTrue(result)


    @patch('services.player_service.update_query')
    def test_edit_is_connected_in_player(self, mock_update_query):

        # Arrange
        mock_update_query.return_value = None

        # Act
        result = player_service.edit_is_connected_in_player(1, 2)

        # Assert
        mock_update_query.assert_called_once_with('''UPDATE players SET is_connected = ? WHERE id = ?''',
                (1, 2))
        self.assertIsNone(result)


    @patch('services.player_service.update_query')
    def test_edit_is_active_in_player(self, mock_update_query):

        # Arrange
        mock_update_query.return_value = None

        # Act
        result = player_service.edit_is_active_in_player(0, 'Bob Ross', 1)

        # Assert
        mock_update_query.assert_called_once_with('''UPDATE players SET is_active = ? WHERE full_name = ? and is_connected = ?''',
                (0, 'Bob Ross', 1))
        self.assertIsNone(result)


    @patch('services.player_service.update_query', side_effect=[None, None])
    @patch('services.player_service.insert_query')
    def test_delete_player(self, mock_insert_query, mock_update_query):

        # Arrange
        mock_insert_query.return_value = None

        # Act
        result = player_service.delete_player(1)

        # Assert
        mock_update_query.assert_has_calls([
        call('''UPDATE users SET role = ? WHERE players_id = ?''', ('spectator', 1)),
        call('''UPDATE users SET players_id = ? WHERE players_id = ?''', (None, 1))
        ])
        mock_insert_query.assert_called_once_with('''DELETE FROM players WHERE id = ?''',
                 (1,))
        self.assertIsNone(result)


    @patch('services.player_service.update_query')
    def test_edit_is_active_in_player_by_id(self, mock_update_query):

        # Arrange
        mock_update_query.return_value = None

        # Act
        result = player_service.edit_is_active_in_player_by_id(1)

        # Assert
        mock_update_query.assert_called_once_with('''UPDATE players SET is_active = ? WHERE id = ? ''',
                (1, 1))
        self.assertIsNone(result)
    

    @patch('services.player_service.update_query')
    def test_back_is_active_in_player_by_id(self, mock_update_query):

        # Arrange
        mock_update_query.return_value = None

        # Act
        result = player_service.back_is_active_in_player_by_id(1)

        # Assert
        mock_update_query.assert_called_once_with('''UPDATE players SET is_active = ? WHERE id = ? ''',
                (0, 1))
        self.assertIsNone(result)


    @patch('services.player_service.read_query')
    def test_get_player_by_full_name_next(self, mock_read_query):

        # Arrange
        mock_read_query.return_value = [(3, 'Bob Ross', 'USA', 'DIVA', 0, 0, None, None)]

        # Act
        result = player_service.get_player_by_full_name_next('Bob Ross')

        # Assert
        mock_read_query.assert_called_once_with(
        'SELECT id, full_name, country, sports_club, is_active, is_connected, teams_id, blocked_players_id FROM players WHERE full_name = ?',
        ('Bob Ross',)
        )
        self.assertTrue(result)


    @patch('services.player_service.read_query')
    def test_do_not_get_player_by_full_name_next(self, mock_read_query):

        # Arrange
        mock_read_query.return_value = []

        # Act
        result = player_service.get_player_by_full_name_next('Bob Ross')

        # Assert
        mock_read_query.assert_called_once_with(
        'SELECT id, full_name, country, sports_club, is_active, is_connected, teams_id, blocked_players_id FROM players WHERE full_name = ?',
        ('Bob Ross',)
        )
        self.assertIsNone(result)


if __name__ == '__main__':
    unittest.main()