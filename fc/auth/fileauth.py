from .auth import Auth
from configparser import ConfigParser
import os


class FileAuth(Auth):
    _file = '~/.fcli'

    def __init__(self):
        self.ini = ConfigParser()
        self.ini.read(os.path.expanduser(self._file))

    def username(self):
        return self.ini.get('default', 'username')

    def password(self):
        return self.ini.get('default', 'password')
