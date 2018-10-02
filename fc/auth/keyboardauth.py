from .auth import Auth
import click


class KeyboardAuth(Auth):
    def __init__(self, username=None):
        self._username = username

    def username(self):
        if self._username is None:
            return click.prompt('Enter your username', type=str)
        else:
            return self._username

    def password(self):
        return click.prompt('Enter your password', type=str, hide_input=True)
