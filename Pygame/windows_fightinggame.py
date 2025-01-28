import pygame
import pygame_menu
import os
import sys
from stadium_fightinggame import Stadium


class GameMenu:
    def __init__(self):
        pygame.init()
        self.res = (900, 900)
        self.screen = pygame.display.set_mode(self.res)
        pygame.display.set_caption("Character Selection Menu")

        self.selected_character = None

    def start_the_game(self):
        """Handle game start"""
        if self.selected_character:
            print(f"Starting game with character: {self.selected_character}")

            pygame.display.quit()
            pygame.quit()

            pygame.init()
            stadium = Stadium(self.selected_character)
            stadium.run()
        else:
            print("Please select a character first!")

    def set_character(self, value, index):
        """Handle character selection"""
        self.selected_character = value[0]  # Store the character name
        print(f"Character selected: {value[0]}, Index: {index}")

    def add_baseimage(self, image_path, scale=(50, 50)):
        """Load and scale an image, with error handling"""
        try:
            # Check if file exists
            if not os.path.exists(image_path):
                raise FileNotFoundError(f"Image file not found: {image_path}")

            base_image = pygame_menu.BaseImage(
                image_path=image_path,
                drawing_mode=pygame_menu.baseimage.IMAGE_MODE_SIMPLE
            )
            base_image.resize(*scale)
            return base_image
        except Exception as e:
            print(f"Error loading image {image_path}: {str(e)}")
            # Return a colored rectangle as fallback
            surface = pygame.Surface(scale)
            surface.fill((255, 0, 0))  # Red rectangle as placeholder
            return pygame_menu.BaseImage(surface)

    def run(self):
        # Create menu theme
        mytheme = pygame_menu.themes.THEME_DARK.copy()
        mytheme.widget_font_size = 20

        # Create the menu
        menu = pygame_menu.Menu(
            'Character Selection',
            650, 300,
            theme=mytheme
        )

        try:
            # Load character images
            characters = [
                ('Lucario', self.add_baseimage("sprites/lucario_sprite.png")),
                ('Zoroark', self.add_baseimage("sprites/zoroark_sprite.png")),
                ('Zeraora', self.add_baseimage("sprites/zeraora_sprite.png")),
                ('Mewtwo', self.add_baseimage("sprites/mewtwo_sprite.png"))
            ]

            # Add widgets to the menu
            menu.add.text_input('Name :', default='Player 1', maxchar=20)

            for char_name, char_image in characters:
                menu.add.image(char_image)

            menu.add.selector(
                'Choose your character:',
                [(char[0], char[1]) for char in characters],
                onchange=self.set_character
            )

            menu.add.vertical_margin(30)  # Add some space
            menu.add.button('Play', self.start_the_game)
            menu.add.button('Quit', pygame_menu.events.EXIT)

            # Main game loop
            menu.mainloop(self.screen)

        except Exception as e:
            print(f"An error occurred: {str(e)}")
            pygame.quit()
            sys.exit()


if __name__ == '__main__':
    game = GameMenu()
    game.run()

