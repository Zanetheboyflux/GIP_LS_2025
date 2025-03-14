import socket
import pickle
import threading
import time
import json
import logging

class GameServer:
    def __init__(self, host='0.0.0.0', port=5555):
        logging.basicConfig(level=logging.INFO,
                            format='%(asctime)s [SERVER] %(message)s',
                            datefmt='%H:%M:%S')
        self.logger = logging.getLogger('GameServer')

        self.host = host
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.clients = {}
        self.client_characters = {}
        self.game_state = {
            'players': {},
            'ready': 0
        }
        self.match_started = False
        self.platforms = []
        self.init_platforms()
        self.logger.info(f'Initializing server on {host}:{port}')

    def init_platforms(self):
        screen_width = 1000
        screen_height = 1000

        platform_width1 = 600
        platform_height = 20
        platform_x1 = (screen_width - platform_width1) // 2
        platform_y1 = 600

        platform_width2 = 100
        platform_x2 = (screen_width - platform_width2) // 2.25
        platform_y2 = 300
        platform_x3 = (screen_width - platform_width2) // 1.75
        platform_y3 = 450

        self.platforms = [
            {'x': platform_x1, 'y': platform_y1, 'width': platform_width1, 'height': platform_height},
            {'x': platform_x2, 'y': platform_y2, 'width': platform_width2, 'height': platform_height},
            {'x': platform_x3, 'y': platform_y3, 'width': platform_width2, 'height': platform_height}
        ]

        self.game_state['platforms'] = self.platforms

    def start(self):
        try:
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(2)
            self.logger.info(f'Server started, listening on {self.host}:{self.port}')
            update_thread = threading.Thread(target=self.update_game_state)
            update_thread_daemon = True
            update_thread.start()

            while True:
                client_socket, address = self.server_socket.accept()
                if len(self.clients)>= 2:
                    self.logger.info(f'Rejected connection from {address} - server full')
                    client_socket.send(pickle.dumps({'status': "error", "message": "Server full"}))
                    client_socket.close()
                    continue
                self.logger.info(f'Connection from {address} has been established')

                player_num = len(self.clients) + 1
                self.clients[player_num] = client_socket

                # self.game_state[player_num]= client_socket
                self.game_state['players'][player_num] = {
                    'connected': True,
                    'character': None,
                    'x': 300 if player_num == 1 else 700,
                    'y': 580,
                    'health': 100,
                    'is_dead': False,
                    'is_attacking': False,
                    'is_special_attacking': False,
                    'facing_right': True if player_num == 2 else False
                }

                client_socket.send(pickle.dumps({'status':'connected', 'player_num': player_num}))
                client_thread = threading.Thread(target=self.handle_client, args=(client_socket, player_num))
                client_thread.daemon = True
                client_thread.start()

        except Exception as e:
            self.logger.error(f'Error starting server: {str(e)}')
        finally:
            self.close_server()

    def handle_client(self, client_socket, player_num):
        try:
            while True:
                data = client_socket.recv(4096)
                if not data:
                    break
                client_data = pickle.loads(data)

                if 'character_select' in client_data:
                    self.game_state['players'][player_num]['character']= client_data['character_select']
                    self.client_characters[player_num] = client_data['character_select']
                    self.logger.info(f'Player {player_num} selected character: {client_data}')

                if 'ready' in client_data and client_data['ready']:
                    self.game_state['ready'] += 1
                    self.logger.info(f"Player {player_num} is ready. Ready count: {self.game_state['ready']}")

                if 'player_action' in client_data:
                    action = client_data['player_action']
                    player = self.game_state['players'][player_num]

                    if 'x' in action:
                        player['x'] = action['x']
                    if 'y' in action:
                        player['y'] = action['y']

                    if 'facing_right' in action:
                        player['facing_right'] = action['facing_right']
                    if 'is_attacking' in action:
                        player['is_attacking'] = action['is_attacking']
                    if 'is_special_attacking' in action:
                        player['is_special_attacking'] = action['is_special_attacking']

                    if 'attack' in action and action['attack']:
                        target_player = 2 if player_num == 1 else 1
                        damage = action['damage'] if 'damage' in action else 10

                        if target_player in self.game_state['players']:
                            target = self.game_state['players'][target_player]
                            distance = abs(player['x'] - target['x'])
                            is_target_right = target['x'] > player['x']

                            attack_range = 200
                            if 'attack_range' in action:
                                attack_range = action['attack_range']
                            if distance <= attack_range and player['facing_right'] == is_target_right:
                                target['health'] = max(0, target['health'] - damage)
                                self.logger.info(f'Player {player_num} hit Player {target_player} for {damage} damage. Health remaining: {target['health']}')

                                if target['health'] <= 0:
                                    target['is_dead'] = True
                                    self.logger.info(f'Player {target_player} has been defeated!')
                    self.broadcast_game_state()

        except Exception as e:
            self.logger.info(f'Error handling client {player_num}:{str(e)}')
        finally:
            self.handle_disconnect(player_num)

    def broadcast_game_state(self):
        for client_socket in self.clients.values():
            try:
                client_socket.send(pickle.dumps(self.game_state))
            except Exception as e:
                self.logger.error(f'Error sending game state: {str(e)}')

    def handle_disconnect(self, player_num):
        print(f'[SERVER] Player {player_num} disconnected')
        if player_num in self.clients:
            try:
                self.clients[player_num].close()
            except Exception:
                pass
            del self.clients[player_num]

        if player_num in self.game_state['players']:
            self.game_state['players'][player_num]['connected'] = False

        if self.match_started:
            self.match_started = False
            self.game_state['ready'] = 0
            self.logger.info('Match ended due to player disconnect')

    def update_game_state(self):
        while True:
            if not self.match_started and self.game_state['ready'] >= 2:
                self.logger.info('Both players ready, starting match!')
                self.match_started = True

                for client_socket in self.clients.values():
                    client_socket.send(pickle.dumps({
                        "status": "match_start",
                        "game_state": self.game_state
                    }))

            if self.match_started:
                game_over = False
                winner = None

                for player_num, player_data in self.game_state['players'].items():
                    if player_data['is_dead']:
                        game_over = True
                        winner = 1 if player_num == 2 else 2
                        break

                if game_over:
                    self.logger.info(f'Game_over! Player {winner} wins!')
                    for client_socket in self.clients.values():
                        client_socket.send(pickle.dumps({
                            "status": 'game_over',
                            'winner': winner,
                            'game_state': self.game_state
                        }))

                self.match_started = False
                self.game_state['ready'] = 0

                for player_num in self.game_state['players']:
                    self.game_state['players'][player_num]['health'] = 100
                    self.game_state['players'][player_num]['is_dead'] = False
                    self.game_state['players'][player_num]['x'] = 300 if player_num == 1 else 700
                    self.game_state['players'][player_num]['y'] = 580

                self.logger.info('Game reset for new match')

            time.sleep(0.05)

    def close_server(self):
        self.logger.info('Closing server')
        for client_socket in self.clients.values():
            try:
                client_socket.close()
            except Exception:
                pass
        self.server_socket.close()

if __name__ == "__main__":
    server = GameServer()
    try:
        server.start()
    except KeyboardInterrupt:
        server.logger.info('Server stopped by user')
        server.close_server()