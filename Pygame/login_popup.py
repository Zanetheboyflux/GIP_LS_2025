import pygame_gui
import pygame
import mysql.connector
from tkinter import messagebox
import tkinter as tk

class LoginPopup:
    def __init__(self, manager, rect, on_success=None):
        self.manager = manager
        self.on_success = on_success
        self.db_config = {
            'host': 'localhost',
            'user': 'root',
            'password': '',
            'database': 'fightinggame_database'
        }

        self.window = pygame_gui.elements.UIWindow(
            rect=rect,
            manager=manager,
            window_display_title = "Login"
        )

        window_rect = self.window.get_container().get_rect()
        padding = 20
        element_width = window_rect.width - (padding * 2)

        pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(padding, padding, element_width, 30),
            text="Username",
            manager=manager,
            container=self.window.get_container()
        )

        self.username_input = pygame_gui.elements.UITextEntryLine(
            relative_rect=pygame.Rect(padding, padding + 35, element_width, 30),
            manager=manager,
            container= self.window.get_container()
        )

        pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(padding, padding + 80, element_width, 30),
            text='Password:',
            manager=manager,
            container=self.window.get_container()
        )

        self.password_input = pygame_gui.elements.UITextEntryLine(
            relative_rect=pygame.Rect(padding, padding +115, element_width, 30),
            manager = manager,
            container= self.window.get_container()
        )
        self.password_input.set_text_hidden(True)

        self.login_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(padding, padding + 165, element_width, 40),
            text="Login",
            manager=manager,
            container=self.window.get_container()
        )

    def process_event(self, event):
        if event.type == pygame.USEREVENT:
            if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                if event.ui_element == self.login_button:
                    self.authenticate()

    def authenticate(self):
        username = self.username_input.get_text()
        password = self.password_input.get_text()

        connection = None
        try:
            root = tk.Tk()
            root.withdraw()

            connection = mysql.connector.connect(**self.db_config)
            cursor = connection.cursor(dictionary=True)
            query = "SELECT * FROM accounts WHERE account_name = %s AND account_password = %s"
            cursor.execute(query, (username, password))

            user = cursor.fetchall()
            if user:
                messagebox.showinfo("Login", f"Welcome, {username}!")
                if self.on_success:
                    self.on_success(user[0])
                self.window.kill()

            else:
                messagebox.showerror("Login Failed", "Invalid username or password")
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f'Error: {err}')
        finally:
            if connection and connection.is_connected():
                cursor.close()
                connection.close()
            try:
                root.destroy()
            except:
                pass

    def kill(self):
        self.window.kill()




