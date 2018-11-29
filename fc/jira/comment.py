import requests
from requests import HTTPError
from requests.auth import HTTPBasicAuth
from ..auth.auth import Auth
from typing import Optional
from pprint import pprint


class Comment:
    api_url = 'https://jira.cms.gov/rest/api/2/issue/'
    base_url = 'https://jira.cms.gov/browse/{}'

    def __init__(self):
        self.id = None
        self.url = None
        self.auth = None
        self.note = None

    def from_args(self, id: str, note: str, auth: Auth):
        self.id = id
        self.note = note
        self.auth = auth

        return self

    def type_str(self) -> str:
        raise NotImplementedError

    def create(self):
        json = {'body': self.note}

        response = requests.post("{}/{}/comment".format(self.api_url, self.id), json=json,
                                 auth=HTTPBasicAuth(self.auth.username(), self.auth.password()))
        response.raise_for_status()

        self.url = self.base_url.format(self.id)

        return self.id, self.url
