class Auth:
    def username(self):
        raise NotImplementedError

    def password(self):
        raise NotImplementedError

    def google_service_acct_creds(self):
        raise NotImplementedError

    def sheet_create_url(self):
        raise NotImplementedError
