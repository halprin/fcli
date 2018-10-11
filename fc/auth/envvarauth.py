from .auth import Auth
import os


class EnvVarAuth(Auth):
    def __init__(self, username=None):
        self._username = username

    def username(self):
        if self._username is None:
            return os.environ['FCLI_USER']
        else:
            return self._username

    def password(self):
        return os.environ['FCLI_PASS']