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

    def google_service_acct_creds(self):
        if not hasattr(self.__class__, '_g_serv_acct_creds'):
            self.__class__._g_serv_acct_creds = click.prompt('Enter path to Google service account credential file',
                                                             type=str)

        return self.__class__._g_serv_acct_creds

    def sheet_create_url(self):
        if not hasattr(self.__class__, '_g_sheet_create_url'):
            self.__class__._g_sheet_create_url = click.prompt('Enter the URL to create a new Google sheet',
                                                             type=str)

        return self.__class__._g_sheet_create_url
