from .auth import Auth
import os


class EnvVarAuth(Auth):
    def username(self):
        return os.environ['FCLI_USER']

    def password(self):
        return os.environ['FCLI_PASS']
