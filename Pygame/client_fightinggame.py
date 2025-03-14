import pygame
import socket
import pickle
import threading
import sys
import time
import logging
from pygame.locals import *

class GameClient:
    def __init__(self, host='localhost', port=5555):
        pygame.init()
        self.host = host
        self.port = port
        self.client_socket = None
        self.player_num = None
        self.character_name = None
        self.opponent_character = None
        self.connected = False
        self.match_started = False
        self.game_over = False
        self.winner = None
        self.character = None

        self.SCREEN_WIDTH = 1000
        self.SCREEN_HEIGHT = 1000
        self.screen = pygame.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
        pygame.display.set_caption("Pokemon Fighting Game - Client")
        self.clock = pygame.time.Clock()
        logging.basicConfig(level=logging.INFO,
                            format='%(asctime)s [CLIENT] %(message)s',
                            datefmt='%H:%M:%S')
        self.logger = logging.getLogger('GameClient')

        self.WHITE = (255, 255, 255)
        self.BLACK = (0, 0, 0)
        self.GRAY = (100, 100, 100)
        self.BLUE = (50, 150, 255)
        self.DARK_BLUE = (30, 30, 120)
        self.RED = (255, 0, 0)
        self.GREEN = (0, 255, 0)

        self.font = pygame.font.Font(None, 74)
        self.small_font = pygame.font.Font(None, 36)

        self.game_state = {
            'players': {},
            'platforms': []
        }
        self.platforms = []
        self.ready = False

        self.available_characters = ['Lucario', 'Mewtwo', 'Zeraora', 'Cinderace']
        self.selected_character_index = 0

        self.character_sprite = None
        self.opponent_sprite = None

    def connect_to_server(self):
        try:
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.connect((self.host, self.port))

            data = self.client_socket.recv(4096)
            response = pickle.loads(data)

            if response['status'] == 'connected':
                self.player_num = response['player_num']
                self.connected = True
                self.logger.info(f'Connected to server as Player {self.player_num}')
                receive_thread = threading.Thread(target=self.receive_data)
                receive_thread.daemon = True
                receive_thread.start()
                return True
            else:
                self.logger.info(f'Failed to connect: {response.get('message', 'Unknown error')}')
                return False
        except Exception as e:
            self.logger.info(f'Error connection to server: {str(e)}')
            return False

    def receive_data(self):
        while self.connected:
            try:
                data = self.client_socket.recv(4096)
                if not data:
                    break
                response = pickle.loads(data)
                if 'status' in response:
                    if response['status'] == 'match_start':
                        self.match_started = True
                        self.game_state = response['game_state']
                        self.init_platforms()
                    elif response['status'] == 'game_over':
                        self.game_over = True
                        self.winner = response['winner']
                else:
                    self.game_state = response

                opponent_num = 2 if self.player_num == 1 else 1
                if (opponent_num in self.game_state['players'] and
                self.game_state['players'][opponent_num]['character'] and
                not self.opponent_character):
                    self.opponent_character = self.game_state['players'][opponent_num]['character']
                    self.opponent_sprite = self.create_character_sprite(self.opponent_character)

            except Exception as e:
                self.logger.info(f'Error receiving data: {str(e)}')
                self.connected = False
                break

    def send_data(self, data):
        try:
            if self.client_socket and self.connected:
                self.client_socket.send(pickle.dumps(data))
        except Exception as e:
            self.logger.info(f'Error sending data: {str(e)}')
            self.connected = False

    def select_character(self):
        selecting = True

        while selecting and self.connected:
            self.screen.fill(self.BLACK)

            title_text = self.font.render(f'Player {self.player_num} - Select Character', True, self.WHITE)
            title_rect = title_text.get_rect(center=(self.SCREEN_WIDTH/2, 100))
            self.screen.blit(title_text, title_rect)

            for i, char_name in enumerate(self.available_characters):
                color = self.GREEN if i == self.selected_character_index else self.WHITE
                char_text = self.small_font.render(char_name, True, color)
                char_rect = char_text.get_rect(center=(self.SCREEN_WIDTH/2, 300 + i*50))
                self.screen.blit(char_text, char_rect)

            instr_text = self.small_font.render('Press UP/DOWN to select, ENTER to confirm', True, self.WHITE)
            instr_rect = instr_text.get_rect(center=(self.SCREEN_WIDTH/2, 600))
            self.screen.blit(instr_text, instr_rect)
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == KEYDOWN:
                    if event.key == K_UP:
                        self.selected_character_index = (self.selected_character_index - 1) % len(self.available_characters)
                    elif event.key == K_DOWN:
                        self.selected_character_index = (self.selected_character_index + 1) % len(self.available_characters)
                    elif event.key == K_RETURN:
                        self.character = self.available_characters[self.selected_character_index]
                        self.send_data({'character_select': self.character})
                        selecting = False
                pygame.display.flip()
                self.clock.tick(60)

    def wait_for_match(self):
        waiting = True
        while waiting and self.connected and not self.match_started:
            self.screen.fill(self.BLACK)

            wait_text = self.font.render('Waiting for opponent...', True, self.WHITE)
            wait_rect = wait_text.get_rect(center=(self.SCREEN_WIDTH/2, 300))
            self.screen.blit(wait_text, wait_rect)

            char_text = self.small_font.render(f'Your character: {self.character}', True, self.GREEN)
            char_rect = char_text.get_rect(center=(self.SCREEN_WIDTH/2, 400))
            self.screen.blit(char_text, char_rect)

            if not self.ready:
                ready_text = self.small_font.render('Press SPACE to ready up', True, self.WHITE)
                ready_rect = ready_text.get_rect(center=(self.SCREEN_WIDTH/2, 500))
                self.screen.blit(ready_text, ready_rect)
            else:
                ready_text = self.small_font.render('You are READY!', True, self.GREEN)
                ready_rect = ready_text.get_rect(center=(self.SCREEN_WIDTH/2, 500))
                self.screen.blit(ready_text, ready_rect)

            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == KEYDOWN and event.key == K_SPACE and not self.ready:
                    self.ready = True
                    self.send_data({'ready': True})

            pygame.display.flip()
            self.clock.tick(60)

    def init_platforms(self):
        if 'platforms' in self.game_state:
            self.platforms = []
            for platform_data in self.game_state['platforms']:
                platform = type('Platform', (), {})
                platform.x = platform_data['x']
                platform.y = platform_data['y']
                platform.width = platform_data['width']
                platform.height = platform_data['height']
                self.platforms.append(platform)

    def draw_background(self):
        for y in range(self.SCREEN_HEIGHT):
            color = (
                self.DARK_BLUE[0] + (self.BLUE[0] - self.DARK_BLUE[0]) * y // self.SCREEN_HEIGHT,
                self.DARK_BLUE[1] + (self.BLUE[1] - self.DARK_BLUE[1]) * y // self.SCREEN_HEIGHT,
                self.DARK_BLUE[2] + (self.BLUE[2] - self.DARK_BLUE[2]) * y // self.SCREEN_HEIGHT
            )
            pygame.draw.line(self.screen, color, (0, y), (self.SCREEN_WIDTH, y))

        pygame.draw.polygon(self.screen, self.GRAY, [(0, self.SCREEN_HEIGHT), (300, 500), (500, self.SCREEN_HEIGHT)])
        pygame.draw.polygon(self.screen, self.GRAY, [(500, self.SCREEN_HEIGHT), (700, 400), (900, self.SCREEN_HEIGHT)])

    def draw_platforms(self):
        for platform in self.platforms:
            pygame.draw.rect(self.screen, self.DARK_BLUE, (platform.x, platform.y, platform.width, platform.height))
            pygame.draw.rect(self.screen, self.WHITE, (platform.x, platform.y, platform.width, 5))

    def create_character_sprite(self, character_name):
        character_colors = {
            'Lucario': (0, 0, 255),
            'Mewtwo': (255, 0, 255),
            'Zeraora': (255, 255, 0),
            'Cinderace': (255, 0, 0)
        }

        try:
            sprite = f"sprites/{character_name.lower()}_sprite.png"
            img = pygame.image.load(sprite).convert_alpha()
            self.logger.info(f'Error making sprite for {sprite}')
            return pygame.transform.scale(img, (100, 100))

        except Exception as e:
            self.logger.info(f"Error loading sprite for {character_name}: {str(e)}")

            surface = pygame.surface.Surface((100, 100))
            color = character_colors.get(character_name, (255, 0, 0))
            surface.fill(color)
            return surface

    def draw_character(self, player_data, sprite):
        if not player_data:
            return

        # Draw the character sprite
        self.screen.blit(sprite, (player_data['x'] - sprite.get_width() // 2,
                                  player_data['y'] - sprite.get_height()))

        # Draw health bar
        bar_width = 100
        bar_height = 10
        bar_x = player_data['x'] - bar_width // 2
        bar_y = player_data['y'] - sprite.get_height() - 20

        pygame.draw.rect(self.screen, self.RED, (bar_x, bar_y, bar_width, bar_height))
        health_width = (player_data['health'] / 100) * bar_width
        if health_width > 0:
            pygame.draw.rect(self.screen, self.GREEN, (bar_x, bar_y, health_width, bar_height))
        pygame.draw.rect(self.screen, self.BLACK, (bar_x, bar_y, bar_width, bar_height), 1)

    def draw_game_over_screen(self):
        overlay = pygame.Surface((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
        overlay.fill(self.BLACK)
        overlay.set_alpha(128)
        self.screen.blit(overlay, (0, 0))

        if self.winner:
            if self.winner == int(self.player_num):
                winner_text = "YOU WIN!"
            else:
                winner_text = "YOU LOSE!"

            text = self.font.render(winner_text, True, self.GREEN)
            text_rect = text.get_rect(center=(self.SCREEN_WIDTH / 2, self.SCREEN_HEIGHT / 2))
            self.screen.blit(text, text_rect)

        exit_text = self.small_font.render("Press ESC to exit", True, self.WHITE)
        exit_rect = exit_text.get_rect(center=(self.SCREEN_WIDTH / 2, self.SCREEN_HEIGHT / 2 + 60))
        self.screen.blit(exit_text, exit_rect)

    def check_on_platform(self, player_x, player_y):

        if player_y >= 580:
            return True

        player_width = 50
        player_half_width = player_width // 2

        for platform in self.platforms:
            if (player_x + player_half_width > platform.x and
            player_x - player_half_width < platform.x + platform.width):
                if abs(player_y - platform.y) < 10:
                    return True

        return False

    def run_game(self):
        if not self.character_sprite and self.character:
            self.character_sprite = self.create_character_sprite(self.character)

        if not self.opponent_sprite:
            self.opponent_sprite = pygame.Surface((100, 100))
            self.opponent_sprite.fill((255, 0, 0))

        opponent_num = 2 if self.player_num == 1 else 1
        if opponent_num in self.game_state['players'] and self.game_state['players'][opponent_num]['character']:
            opponent_character = self.game_state['players'][opponent_num]['character']
            if not self.opponent_character or self.opponent_character != opponent_character:
                self.opponent_character = opponent_character
                self.opponent_sprite = self.create_character_sprite(opponent_character)

        running = True
        last_attack_time = 0
        last_special_attack_time = 0
        special_attack_cooldown = 3000
        is_jumping = False
        jump_velocity = 0
        gravity = 1
        jump_strength = 15
        player_width = 50

        while running and self.connected:
            current_time = pygame.time.get_ticks()

            for event in pygame.event.get():
                if event.type == QUIT:
                    running = False
                    pygame.quit()
                    sys.exit()
                if event.type == KEYDOWN and event.key == K_ESCAPE:
                    running = False

            self.screen.fill(self.BLACK)
            self.draw_background()
            self.draw_platforms()

            if self.game_over:
                if self.player_num in self.game_state['players']:
                    self.draw_character(self.game_state['players'][self.player_num], self.character_sprite)

                opponent_num = 2 if self.player_num == 1 else 1
                if opponent_num in self.game_state['players']:
                    self.draw_character(self.game_state['players'][opponent_num], self.opponent_sprite)

                self.draw_game_over_screen()

            elif self.match_started:
                keys = pygame.key.get_pressed()

                if self.player_num not in self.game_state['players']:
                    continue

                player_data = self.game_state['players'][self.player_num]

                action = {}

                if self.player_num == 1:
                    left_key = K_q
                    right_key = K_d
                    jump_key = K_z
                    attack_key = K_a
                    special_attack_key = K_e
                else:
                    left_key = K_LEFT
                    right_key = K_RIGHT
                    jump_key = K_UP
                    attack_key = K_k
                    special_attack_key = K_l

                if keys[left_key]:
                    if 'x' in player_data:
                        player_data['x'] = max(50, player_data['x']-5)
                        action['x'] = player_data['x']
                        action['facing_right'] = False

                elif keys[right_key]:
                    if 'x' in player_data:
                        player_data['x'] = min(950, player_data['x']+5)
                        action['x'] = player_data['x']
                        action['facing_right'] = True

                on_platform = self.check_on_platform(player_data.get('x', 0), player_data.get('y', 0))

                if player_data.get('y', 0) >= 580:
                    on_platform = True

                if not on_platform:
                    for platform in self.platforms:
                        if (player_data.get('x', 0) + player_width > platform.x and
                        player_data.get('x', 0) - player_width < platform.x + platform.width and
                        abs(player_data.get('y', 0) - platform.y) <10):
                            on_platform = True
                            break

                if keys[jump_key] and on_platform and not is_jumping:
                    is_jumping = True
                    jump_velocity = -jump_strength

                if is_jumping or not on_platform:
                    player_data['y'] += jump_velocity
                    jump_velocity += gravity
                    action['y'] = player_data['y']

                    if self.check_on_platform(player_data.get('x', 0), player_data.get('y', 0)) and jump_velocity > 0:
                        is_jumping = False
                        jump_velocity = 0

                        for platform in self.platforms:
                            if (player_data.get('x', 0) + 50 > platform.x and
                            player_data.get('x', 0) - 50 < platform.x + platform.width and
                            abs(player_data.get('y', 0) - platform.y)<15):
                                player_data['y'] = platform.y
                                action['y'] = platform.y
                                break

                        if player_data.get('y', 0) > 580:
                            player_data['y'] = 580
                            action['y'] = 580

                if keys[attack_key] and current_time - last_attack_time > 500:
                    action['is_attacking'] = True
                    action['attack'] = True
                    action['damage'] = 10
                    action['attack_range'] = 150
                    last_attack_time = current_time

                if keys[special_attack_key] and current_time - last_special_attack_time:
                    action['is_special_attacking'] = True
                    action['attack'] = True

                    if self.character == 'Lucario':
                        health_percent = player_data.get('health', 100) / 100
                        action['damage'] = 25 * (1 + (1 - health_percent))
                        action['attack_range'] = 200
                    elif self.character == 'Mewtwo':
                        action['damage'] = 30
                        action['attack_range'] = 300
                    elif self.character == 'Zeraora':
                        action['damage'] = 20
                        action['attack_range'] = 150
                    elif self.character == 'Cinderace':
                        opponent_num = 2 if self.player_num == 1 else 1
                        opponent_data = self.game_state['players'].get(opponent_num, {})
                        if opponent_data:
                            distance = abs(player_data.get('x', 0) - opponent_data.get('x', 0))
                            action['damage'] = 22 * (1 + distance / 250)
                            action['attack_range'] = 250

                    last_special_attack_time = current_time

                if action:
                    self.send_data({'player_action': action})

                if self.player_num in self.game_state['players']:
                    self.draw_character(self.game_state['players'][self.player_num], self.character_sprite)

                opponent_num = 2 if self.player_num == 1 else 1
                if opponent_num in self.game_state['players']:
                    self.draw_character(self.game_state['players'][opponent_num], self.opponent_sprite)

            pygame.display.flip()
            self.clock.tick(60)


    def run(self):
        if self.connect_to_server():
            self.select_character()
            self.wait_for_match()
            self.run_game()

            if self.client_socket:
                self.client_socket.close()
        else:
            self.logger.info('Failed to connect to server')
            pygame.quit()
            sys.exit()

if __name__ == '__main__':
    client = GameClient(host='localhost', port=5555)
    client.run()




