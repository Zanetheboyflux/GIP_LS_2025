from pgu import gui
import mysql.connector
import tkinter as tk
from tkinter import messagebox

class LoginPopup(gui.Dialog):
    def __init__(self, on_success=None, **params):
        self.on_success = on_success
        self.db_config = {
            'host': 'localhost',
            'user': 'root',
            'password': '',
            'database': 'fightinggame_database'
        }

        title = gui.Label("Login")
        main = gui.Table(width=500, height=250)

        username_label = gui.Label('Username:')
        self.username_input = gui.Input(size=20)

        password_label = gui.Label('Password:')
        self.password_input = gui.Input(size=20, password=True)

        btn = gui.Button('Login')
        btn.connect(gui.CLICK, self.authenticate, None)

        main.tr()
        main.td(username_label)
        main.td(self.username_input)
        main.tr()
        main.td(password_label)
        main.td(self.password_input)
        main.tr()
        main.td(btn, colspan=2)

        gui.Dialog.__init__(self, title, main)

    def authenticate(self, _):
        username = self.username_input.value
        password = self.password_input.value

        try:
            connection = mysql.connector.connect(**self.db_config)
            cursor = connection.cursor(dictionary=True)
            query = "SELECT * FROM accounts where account_name = %s AND account_password = %s"
            cursor.execute(query, (username, password))

            user = cursor.fetchall()
            if user:
                messagebox.showinfo("Login", f"Welcome, {username}!")
                if self.on_success:
                    self.on_success(user[0])
                self.close()
            else:
                messagebox.showerror("Login Failed", "Invalid username or password")
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f'Error: {err}')

        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()




