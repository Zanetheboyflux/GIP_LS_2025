import pygame
import os

class Character:
    def __init__(self, name, x, y):
        self.name = name
        self.x = x
        self.y = y
        self.sprite = self.load_sprite()
        self.scale = (50, 50)

    def load_sprite(self):

        character_colors = {
            'Lucario': (0, 0, 255),
            'Mewtwo': (255, 0, 255),
            'Zeraora': (255, 255, 0),
            'Zoroark': (255, 0, 0)
        }

        try:
            base_sprite = pygame.Surface((64, 64), pygame.SRCALPHA)
            sprite_path = f"sprites/{self.name.lower()}_sprite.png"
            if self.name == 'Lucario':
                colors = {
                    'main': (30, 144, 255),
                    'dark': (47, 47, 47),
                    'spike': (0, 0, 0),
                    'chest': (255, 223, 0)
                }
                pixel_data = self.get_lucario_pixels()

            elif self.name == 'Mewtwo':
                colors = {
                    'main': (255, 255, 255),
                    'detail': (147, 112, 219),
                    'shadow': (200, 200, 200)
                }
                pixel_data = self.get_mewtwo_pixels()

            elif self.name == 'Zeraora':
                colors = {
                    'main': (255, 255, 224),
                    'dark': (169, 169, 169),
                    'detail': (0, 191, 255)
                }
                pixel_data = self.get_zeraora_pixels()

            elif self.name == 'Zoroark':
                colors = {
                    'main': (47, 47, 47),
                    'detail': (220, 20, 60),
                    'accent': (169, 169, 169)
                }
                pixel_data = self.get_zoroark_pixels()

                scaled_sprite = pygame.transform.scale(base_sprite, self.scale)

        except Exception as e:
            print(f"Error loading sprite for {self.name}: {str(e)}")
            color = character_colors.get(self.name, (255, 0, 0))
            surface = pygame.Surface(self.scale)
            surface.fill(color)
            return surface

    def draw(self, screen):
        if self.sprite:
            screen.blit(self.sprite, (self.x - self.sprite.get_width()//2,
                                      self.y - self.sprite.get_height()))

class CharacterManager:
    def __init__(self):
        self.current_character = None

    def set_character(self, character_name):
        character_x = 500
        character_y = 580
        self.current_character = Character(character_name, character_x, character_y)

    def draw(self, screen):
        if self.current_character:
            self.current_character.draw(screen)