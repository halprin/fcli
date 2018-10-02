from .auth import Auth
from .fileauth import FileAuth
from .keyboardauth import KeyboardAuth


class ComboAuth(Auth):
    def __init__(self, username):
        self._username = username

    def username(self):
        if self._username is not None:
            return self._username

        try:
            return FileAuth().username()
        except Exception:
            return KeyboardAuth().username()

    def password(self):
        if self._username is not None:
            return KeyboardAuth().password()

        try:
            return FileAuth().password()
        except Exception:
            return KeyboardAuth().password()
