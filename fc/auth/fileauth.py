from .auth import Auth
from configparser import ConfigParser
import os


class FileAuth(Auth):
    _file = '~/.fcli/.fcli-creds'

    def __init__(self):
        self.ini = ConfigParser()
        self.ini.read(os.path.expanduser(self._file))

    def username(self):
        return self.ini.get('default', 'username')

    def password(self):
        return self.ini.get('default', 'password')

    def google_service_acct_creds(self):
        return self.ini.get('gapps', 'service-acct-creds')

    def sheet_create_url(self):
        return self.ini.get('gapps', 'sheet-create-url')
