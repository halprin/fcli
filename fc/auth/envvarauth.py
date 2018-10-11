from .auth import Auth
import os


class EnvVarAuth(Auth):
    def __init__(self, username=None):
        if username is None:
            self._username = os.environ['FCLI_USER']
        else:
            self._username = username
        self._password = os.environ['FCLI_PASS']

    def username(self):
        return self._username

    def password(self):
        return self._password