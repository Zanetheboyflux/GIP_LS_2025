import pygame
import pygame_gui
import logging
class LoginPopup:
    def __init__(self):
        logging.basicConfig(level=logging.INFO,
                            format='%(asctime)s [CLIENT] %(message)s',
                            datefmt='%H:%M:%S')
        self.logger = logging.getLogger('GameClient')

        self.manager = None
        self.screen = None
        self.input_field = None
        self.button = None
        self.running = False

    def login_success_handler(self, user_data):
        self.logger.info(f"User logged in: {user_data['account_name']}")
        self.start()

    def show_popup(self, manager, window_rect):
        popup_rect = pygame.Rect(window_rect.centerx - 150, window_rect.centery - 75, 300, 150)
        popup_window = pygame_gui.elements.UIPanel(popup_rect, manager=manager)

        input_rect = pygame.Rect(50, 30, 200, 30)
        input_field = pygame_gui.elements.UITextEntryLine(relative_rect=input_rect, container=popup_window,
                                                          manager=manager)

        button_rect = pygame.Rect(100, 80, 100, 30)
        button = pygame_gui.elements.UIButton(relative_rect=button_rect, text='Submit', container=popup_window,
                                              manager=manager)

        return input_field, button


    def create_login_popup(self):
        pygame.init()
        manager = pygame_gui.UIManager((1000, 800))
        screen = pygame.display.set_mode((1000, 800))
        input_field, button = self.show_popup(manager, screen.get_rect())

        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame_gui.UI_BUTTON_PRESSED and event.ui_element == button:
                    print("Input Value:", input_field.get_text())

                manager.process_events(event)

            manager.update(0.016)  # Approximate frame time
            # screen.fill((0, 0, 0))
            # manager.draw_ui(screen)
            pygame.display.update()

        # pygame.quit()

    def start(self):
        self.logger.info("Starting application after succesful login")




