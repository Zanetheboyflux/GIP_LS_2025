import pickle
import sqlite3
import mysql.connector
import logging
import os
import time
from typing import Dict, Any, Optional, Tuple

class GameDatabase:
    def __init__(self, db_type="sqlite", db_path="fightinggame_database.db",
                 mysql_config=None):
        """
        Args:
        :param db_type (str): "sqlite" or "mysql"
        :param db_path (str): Path to the SQLite database file
        :param mysql_config(dict): MySQL connection parameters
        """

        logging.basicConfig(level=logging.INFO,
                            format='%(asctime)s [DATABASE]%(message)s',
                            datefmt='%H:%M:%S')
        self.logger = logging.getLogger('GameDatabase')

        self.db_type = db_type
        self.db_path = db_path

        self.mysqlconfig = mysql_config or {
            'host' : 'localhost',
            'user' : 'root',
            'password' : '',
            'database': 'fightinggame_database'
        }
        self.connection = None
        self.initialize_database()
        self.login_popup = None

    def initialize_database(self):
        try:
            self.connect()
            if self.connection:
                cursor = self.connection.cursor()

                if self.db_type == 'sqlite':
                    cursor.execute(''' CREATE TABLE IF NOT EXISTS pygame (
                    GameID INTEGER PRIMARY KEY AUTOINCREMENT,
                    Winner INTEGER, 
                    Loser INTEGER, 
                    Player1_character TEXT, 
                    Player2_character TEXT, 
                    Timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)
                    ''')

                self.connection.commit()
                self.logger.info('Database initialized succesfully')
            else:
                self.logger.error('Failed to establish database connection')
        except Exception as e:
            self.logger.error(f'Error initializing database: {str(e)}')
        finally:
            self.disconnect()

    def connect(self):
        try:
            if self.db_type == 'sqlite':
                self.connection = sqlite3.connect(self.db_path)
                return True
            elif self.db_type == 'mysql':
                self.connection = mysql.connector.connect(**self.mysqlconfig)
                return True
        except Exception as e:
            self.logger.error(f'Error connection to database: {str(e)}')
            return False

    def disconnect(self):
        if self.connection:
            self.connection.close()
            self.connection = None

    def record_game_result(self, winner: int, loser: int, Player1_character: str, Player2_character: str) -> bool:
        try:
            self.connect()
            cursor = self.connection.cursor()

            query = '''
            INSERT INTO fightinggame_database (Winner, Loser, Player1_character, Player2_character)
            VALUES (?, ?, ?, ?)
            '''
            if self.db_type == "mysql":
                query = query.replace('?', '%s')

            cursor.execute(query, (winner, loser, Player1_character, Player2_character))
            self.connection.commit()

            self.logger.info(f'Game recorded: Winner={winner}, Loser={loser}, P1={Player1_character}, P2= {Player2_character}')
            return True
        except Exception as e:
            self.logger.error(f'Error recording game result: {str(e)}')
            return False

        finally:
            self.disconnect()

    def get_character_stats(self, character_name: str) -> Dict[str, Any]:
        """
        Args:
        :param character_name (str): Name of the character
        Returns:
        dict: Character statistics
        """
        stats = {
            'total_games': 0,
            'wins': 0,
            'losses': 0,
            'win_rate': 0.0
        }
        try:
            self.connect()
            cursor = self.connection.cursor()

            cursor.execute('''
            SELECT COUNT(*) FROM fightinggame_database
            WHERE Player1_character = ?
            ''', (character_name,))

            player1_count = cursor.fetchtone()[0]

            cursor.execute('''
            SELECT COUNT(*) FROM fightinggame_database
            WHERE Player2_character = ?
            ''', (character_name,))

            player2_count = cursor.fetchtone()[0]

            cursor.execute('''
            SELECT COUNT(*) FROM fightinggame_database
            WHERE (Winner = 1 AND Player1_character = ?) 
            or (Winner = 2 AND Player2_character = ?''')
            wins = cursor.fetchtone()[0]

            total_games = player1_count + player2_count
            stats['total_games'] = total_games
            stats['wins'] = wins
            stats['losses'] = total_games - wins
            stats['win_rate'] = (wins / total_games * 100) if total_games > 0 else 0
            return stats
        except Exception as e:
            self.logger.error(f"Error getting character stats: {str(e)}")
            return stats
        finally:
            self.disconnect()

    def get_recent_games(self, limit: int = 10) -> list:
        """
        Args:
        :param limit (int): Maximum number of games to return
        :return:
        list: Recent games data
        """
        games = []
        try:
            self.connect()
            cursor = self.connection.cursor()
            cursor.execute(''' 
            SELECT GameID, Winner, Loser, Player1_character, Player2_character 
            FROM fightinggame_database
            ORDER BY Timestamp DESC
            LIMIT ?''',
                           (limit,))

            columns = ['GameID', 'winner', 'loser', 'player1_character', 'player2_character', 'timestamp']

            for row in cursor.fetchall():
                game_data = dict(zip(columns, row))
                games.append(game_data)
                return games
        except Exception as e:
            self.logger.error(f'Error getting recent games: {str(e)}')
            return games
        finally:
            self.disconnect()

class DatabaseUpdater:
    def __init__(self, db: GameDatabase):
        """
        args:
        :param db (GameDatabase): Database handler instance
        """
        self.db = db
        self.logger = logging.getLogger('DatabaseUpdater')

    def update_from_game_state(self, game_state: Dict[str, Any], winner: int):
        """
        args:
        :param game_state (dict): Current game state from the server
        :param winner (int): Player number who won (1 or 2)
        :return:
        bool: True if succesful, False otherwise
        """
        try:
            if 'players' not in game_state:
                self.logger.error("Invalid game state: 'players' not found")
                return False

            players = game_state['players']

            if 1 not in players or 2 not in players:
                self.logger.error("Invalid game state: player data missing")
                return False

            player1 = players[1]
            player2 = players[2]

            if 'character' not in player1 or 'character' not in player2:
                self.logger.error("Invalid game state: character data missing")
                return False

            player1_character = player1['character']
            player2_character = player2['character']

            loser = 2 if winner == 1 else 1

            return self.db.record_game_result(
                winner = winner,
                loser = loser,
                Player1_character = player1_character,
                Player2_character = player2_character
            )
        except Exception as e:
            self.logger.error(f"Error updating database from game state: {str(e)}")
            return False

class ServerDatabaseHandler:
    def __init__(self, db_config=None):
        """
        Args:
         db_config (dict): Database configuration
         """
        self.update = None
        self.db_config = db_config or {
            'db_type': 'sqlite',
            'db_path': 'game_database.db'
        }
        self.db = GameDatabase(**self.db_config)
        self.updater = DatabaseUpdater(self.db)
        self.logger = logging.getLogger('ServerDatabaseHandler')

    def handle_game_over(self, game_state: Dict[str, Any], winner:int)-> None:
        """
        args:
        :param game_state (dict): current game state
        :param winner (int): Player number who won (1 or 2)
        """
        try:
            success = self.update.update_from_game_state(game_state, winner)
            if success:
                self.logger.info(f"Succesfully recorded game result (Winner: Player {winner}")
            else:
                self.logger.error("Failed to record game result")
        except Exception as e:
            self.logger.error(f'Error handling game over: {str(e)}')

def integrate_with_server(server_instance):
    """
    args:
    :param server_instance: The game server instance
    """
    db_handler = ServerDatabaseHandler()
    original_update = server_instance.update_game_state

    def update_game_state_with_db():
        while True:
            if not server_instance.match_started and server_instance.game_state['ready'] >= 2:
                server_instance.logger.info("Both players ready, starting match!")
                server_instance.match_started = True

                for client_socket in server_instance.clients.values():
                    client_socket.send(pickle.dumps({
                        "status": "match started",
                        "game state": server_instance.game_state
                    }))

            if server_instance.match_started:
                server_instance.broadcast_game_state()
                game_over = False
                winner = None

                for player_num, player_data in server_instance.game_state['players'].items():
                    if player_data['is_dead']:
                        game_over = True
                        winner = 1 if player_num == 2 else 2

                if game_over:
                    server_instance.logger.info(f'Game over! Player {winner} wins!')
                    db_handler.handle_game_over(server_instance.game_state, winner)
                    for client_socket in server_instance.clients.values():
                        client_socket.send(pickle.dumps({
                            "status": "game_over",
                            'winner': winner,
                            'game_state': server_instance.game_state
                        }))
                    server_instance.match_started = False
                    server_instance.game_state['ready'] = 0

                    for player_num, player in server_instance.game_state['players'].items():
                        player.update({
                            'health': 100,
                            'is_dead': False,
                            'x': 300 if player_num == 1 else 700,
                            'y': 580
                        })
                        server_instance.logger.info('Game reset for new match')
                time.sleep(0.05)

            server_instance.update_game_state = update_game_state_with_db()
            return db_handler

if __name__ == "__main__":
    test_db = GameDatabase(db_type='sqlite', db_path='test_game_database.db')
    test_db.record_game_result(
        winner=1,
        loser=2,
        Player1_character="Lucario",
        Player2_character='Mewtwo'
    )

    lucario_stats = test_db.get_character_stats("lucario")
    print(f"Lucario stats: {lucario_stats}")

    recent_games = test_db.get_recent_games(5)
    print(f"Recent games: {recent_games}")

    print('Database test completed')