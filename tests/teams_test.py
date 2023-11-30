import unittest
from unittest.mock import patch, Mock, call
from my_models.model_team import Team
from my_models.model_player import Player
from services import team_service
from fastapi.responses import JSONResponse


class TeamsTests(unittest.TestCase):


    @patch('services.team_service.read_query')
    def test_team_name_exists(self, mock_read_query):

        # Arrange
        mock_read_query.return_value = [('Team Cherries',)]

        # Act
        result = team_service.team_name_exists('Team Cherries')

        # Assert
        mock_read_query.assert_called_once_with(
            'SELECT team_name FROM teams WHERE team_name = ?',
            ('Team Cherries',)
        )
        self.assertTrue(result)


    @patch('services.team_service.read_query')
    def test_team_name_does_not_exist(self, mock_read_query):

        # Arrange
        mock_read_query.return_value = []

        # Act
        result = team_service.team_name_exists('Team Cherries')

        # Assert
        mock_read_query.assert_called_once_with(
            'SELECT team_name FROM teams WHERE team_name = ?',
            ('Team Cherries',)
        )
        self.assertFalse(result)


    @patch('services.team_service.read_query')
    def test_team_id_exists(self, mock_read_query):

        # Arrange
        mock_read_query.return_value = [(1,)]

        # Act
        result = team_service.team_id_exists(1)

        # Assert
        mock_read_query.assert_called_once_with(
            'SELECT id FROM teams WHERE id = ?',
            (1,)
        )
        self.assertTrue(result)


    @patch('services.team_service.read_query')
    def test_team_id_does_not_exist(self, mock_read_query):

        # Arrange
        mock_read_query.return_value = []

        # Act
        result = team_service.team_id_exists(1)

        # Assert
        mock_read_query.assert_called_once_with(
            'SELECT id FROM teams WHERE id = ?',
            (1,)
        )
        self.assertFalse(result)


    @patch('services.team_service.insert_query')
    def test_create_team(self, mock_insert_query):

        # Arrange
        mock_insert_query.return_value = 3

        # Act
        result = team_service.create_team('Team Blue', 3, 2)

        # Assert
        mock_insert_query.assert_called_once_with(
            'INSERT INTO teams(team_name, number_of_players, owners_id) VALUES (?,?,?)',
            ('Team Blue', 3, 2))
        self.assertIsInstance(result, Team)
        self.assertEqual(result.id, 3)
        self.assertEqual(result.team_name, 'Team Blue')
        self.assertEqual(result.number_of_players, 3)
        self.assertEqual(result.owners_id, 2)


    @patch('services.team_service.read_query')
    def test_get_all_teams(self, mock_read_query):

        # Arrange
        mock_read_query.return_value = [(1, 'Team Cherries', 3, 2), (2, 'Team Berries', 3, 3)]

        # Act
        result = team_service.get_all_teams()

        # Assert
        mock_read_query.assert_called_once_with(
            'SELECT id, team_name, number_of_players, owners_id FROM teams'
            )
        self.assertIsNotNone(result)


    @patch('services.team_service.read_query_additional')
    @patch('services.team_service.read_query')
    def test_get_team_and_players_by_id(self, mock_read_query, mock_read_query_additional):
        
        # Arrange
        team_query_result = (3, 'Cherries', 3, 2)
        players_query_result = [
            ('13', 'Carlos Rodriguez', 'Jamaica', 'NeverBackDown', 0, 0, 3, None),
            ('14', 'Camille Dupont', 'France', 'La Sport Club', 0, 0, 3, None)
        ]
        mock_read_query_additional.return_value = team_query_result
        mock_read_query.return_value = players_query_result

        # Act
        result = team_service.get_team_and_players_by_id(3)

        # Assert
        mock_read_query_additional.assert_called_once_with('SELECT id, team_name, number_of_players, owners_id FROM teams where id = ?', (3,))
        mock_read_query.assert_called_once_with('SELECT * FROM players where teams_id = ?', (3,))

        expected_result = Team(
            id=3,
            team_name='Cherries',
            number_of_players=3,
            owners_id=2,
            players=[
                Player(id=13, full_name='Carlos Rodriguez', country='Jamaica', sports_club='NeverBackDown',
                       is_active=0, is_connected=0, teams_id=3, blocked_players_id=None),
                Player(id=14, full_name='Camille Dupont', country='France', sports_club='La Sport Club',
                       is_active=0, is_connected=0, teams_id=3, blocked_players_id=None)
            ])
        self.assertEqual(result, expected_result)


    @patch('services.team_service.update_query')
    @patch('services.team_service.insert_query')
    def test_delete_team(self, mock_insert_query, mock_update_query):

        # Arrange
        mock_insert_query.return_value = []

        # Act
        result = team_service.delete_team(2)

        # Assert
        mock_update_query.assert_called_once_with(
            'UPDATE players SET teams_id = ? WHERE teams_id = ?',
                 (None, 2))
        mock_insert_query.assert_called_once_with(
            'DELETE FROM teams WHERE id = ?',
                 (2,))
        self.assertIsNone(result)


    @patch('services.team_service.read_query')
    def test_teams_list_exists(self, mock_read_query):

        # Arrange
        mock_read_query.return_value = [(3, 'Team Cherries', 2, 2), (4, 'Team Berries', 2, 3)]

        # Act
        result = team_service.teams_list_exists()

        # Assert
        mock_read_query.assert_called_once_with(
            'SELECT id, team_name, number_of_players, owners_id FROM teams',
        )
        self.assertTrue(result)


    @patch('services.team_service.read_query')
    def test_teams_list_does_not_exist(self, mock_read_query):

        # Arrange
        mock_read_query.return_value = [()]

        # Act
        result = team_service.teams_list_exists()

        # Assert
        mock_read_query.assert_called_once_with(
            'SELECT id, team_name, number_of_players, owners_id FROM teams',
        )
        self.assertFalse(result)


    @patch('services.team_service.read_query_additional')
    @patch('my_models.model_team.Team.from_query_result_additional')
    def test_get_team_by_name(self, mock_from_query_result, mock_read_query):
        # Arrange
        mock_read_query.return_value = [(3, 'Team Cherries', 2, 2)]

        # Act
        result = team_service.get_team_by_name('Team Cherries')

        # Assert
        mock_read_query.assert_called_once_with(
            'SELECT id, team_name, number_of_players, owners_id FROM teams where team_name = ?',
            ('Team Cherries',)
        )
        mock_from_query_result.assert_called_once_with((3, 'Team Cherries', 2, 2))
        self.assertTrue(result)


    @patch('services.team_service.read_query_additional')
    def test_do_not_get_team_by_name(self, mock_read_query):

        # Arrange
        mock_read_query.return_value = None

        # Act
        result = team_service.get_team_by_name('Team Cherries')

        # Assert
        mock_read_query.assert_called_once_with(
            'SELECT id, team_name, number_of_players, owners_id FROM teams where team_name = ?',
            ('Team Cherries',)
        )
        expected_response = JSONResponse(status_code=404, content='Team with name: Team Cherries does not exist.')
        self.assertEqual(result.status_code, expected_response.status_code)
        self.assertEqual(result.body, expected_response.body)


if __name__ == '__main__':
    unittest.main()