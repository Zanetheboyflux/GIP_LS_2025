import socket
import pickle
import threading
import time
import pygame
import sys


class GameServer():
    def __init__(self, host='0.0.0.0', port=5555):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((host, port))
        self.server.listen(2)
        self.players = {}
        self.game_state = {
            'player 1': {'character': None, 'x': 300, 'y': 580, 'health': 100, 'is_attacking': False},
            'player 2': {'character': None, 'x': 700, 'y': 580, 'health': 100, 'is_attacking': False},
        }
        print(f'Server started on {host}:{port}')

    def handle_client(self, conn, player_num):
        player_id = f'player{player_num}'
        try:
            conn.send(str(player_num).encode())

            while True:
                try:
                    data = conn.recv(2048)
                    if not data:
                        break
                    play.game_state[player_id].update(player_data)

                    conn.send(pickle.dumps(self.game_state))
                except:
                    break

        finally:
            print(f"{player_id} disconnected")

    def run(self):
        player_count = 1
        while True:
            conn, addr = self.server.accept()
            print(f'Connected to: {addr}')

            if player_count <= 2:
                thread = threading.Thread(target=self.handle_client, args=(conn, player_count))
                self.players[f'player{player_count}'] = conn
                thread.start()
                player_count += 1

            if player_count > 2:
                player_count = 1

class NetworkClient:
    def __init__(self, host='localhost', port=5555):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.host = host
        self.port = port
        self.player_num = self.connect()

    def connect(self):
        try:
            self.client.connect((self.host, self.port))
            return int(self.client.recv(2048).decode())
        except:
            pass

    def send(self, data):
        try:
            self.client.send(pickle.dumps(data))
            return pickle.loads(sqelf.client.recv(2048))
        except socket.error as e:
            print(e)

class NetworkCharacter(Character):
    def __init__(self, name, x, y, network_client):
        super().__init__(name, x, y)
        self.network_client = network_client
        self.player_num = network_client.player_num

        def update_network(self):
            data = {
                'character': self.name,
                'x': self.x,
                'y': self.y,
                'health': self.current_health,
                'is_attacking': self.is_attacking
            }

        game_state = self.network_client.send(data)

        other_player = 'player2' if self.player_num == 1 else 'player1'
        if game_state and other_player in game_state:
            other_data = game_state[other_player]
            return other_data
        return None

class NetworkStadium(Stadium):
    def __init__ (self, player1_character, player2_character, network_client):
        super().__(player1_character, player2_character)
        self.network_client = network_client
        self.player_num = network_client.player_num

        if self.player_num == 1:
            self.character_manager.set_character(player1_character, True)
            self.character_manager.player1 = NetworkCharacter(player1_character, 300, 580, network_client)
        else:
            self.character_manager.set_character(player2_character, False)
            self.character_manager.player2 = NetworkCharacter(player2_character, 700, 580, network_client)

    def update_network(self):
        if self.player_num == 1 and self.character_manager.player1:
            other_data = self.character_manager.player1.update_network()
            if other_data and self.character_manager.player2:
                self.character_manager.player2.x = other_data['x']
                self.character_manager.player2.y = other_data['y']
                self.character_manager.player2.current_health = other_data['health']
                self.character_manager.player2.is_attacking = other_data['is_attacking']

        elif self.player_num == 2 and self.character_manager.player2:
            other_data = self.character_manager.player2.update_network()
            if other_data and self.character_manager.player1:
                self.character_manager.player1.x = other_data['x']
                self.character_manager.player1.y = other_data['y']
                self.character_manager.player1.current_health = other_data['health']
                self.character_manager.player1.is_attacking = other_data['is_attacking']

    def run(self):
        running = True
        clock = pygame.time.Clock()

        while running:
            current_time = pygame.time.get_ticks()

            for event in pygame.event.get()
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    running = False

            keys = pygame.key.get_pressed()
            self.character_manager.update(keys, self.platforms, current_time)
            self.update_network()

            self.screen.fill(self.BLACK)
            self.draw_background()
            self.draw_platform()
            self.character_manager.draw(self.screen)

            if ((self.character_manager.player1 and self.character_manager.player1.is_dead) or
                    (self.character_manager.player2 and self.character_manager.player2.is_dead)):
                self.draw_game_over_screen()

            pygame.display.flip()
            clock.tick(60)

        pygame.quit()
        sys.exit()
