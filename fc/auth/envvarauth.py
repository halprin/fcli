from .auth import Auth
import os


class EnvVarAuth(Auth):

    def username(self):
        return os.environ['FCLI_USER']

    def password(self):
        return os.environ['FCLI_PASS']

    def google_service_acct_creds(self):
        return os.environ['FCLI_G_SERV_ACCT_CREDS']

    def sheet_create_url(self):
        return os.environ['FCLI_G_SHEET_CREATE_URL']
