from .auth import Auth
import click


class KeyboardAuth(Auth):
    def username(self):
        if not hasattr(self.__class__, '_username'):
            self.__class__._username = click.prompt('Enter your username', type=str)

        return self.__class__._username

    def password(self):
        if not hasattr(self.__class__, '_password'):
            self.__class__._password = click.prompt('Enter your password', type=str, hide_input=True)

        return self.__class__._password
