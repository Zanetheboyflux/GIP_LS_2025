import pygame
import os

class Character:
    def __init__(self, name, x, y):
        self.name = name
        self.x = x
        self.y = y
        self.scale = (100, 100)
        self.sprite = self.load_sprite()

    def load_sprite(self):

        character_colors = {
            'Lucario': (0, 0, 255),
            'Mewtwo': (255, 0, 255),
            'Zeraora': (255, 255, 0),
            'Pikachu': (255, 0, 0)
        }

        try:
            sprite_path = f"sprites/{self.name.lower()}_sprite.png"
            img = pygame.image.load(sprite_path).convert_alpha()
            return pygame.transform.scale(img, self.scale)

        except Exception as e:
            print(f"Error loading sprite for {self.name}: {str(e)}")

            surface = pygame.surface.Surface(self.scale)
            color = character_colors.get(self.name, (255, 0, 0))
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