import requests
from requests.auth import HTTPBasicAuth
from ..auth.auth import Auth


class Task:
    api_url = 'https://jira.cms.gov/rest/api/2/issue/'
    base_url = 'https://jira.cms.gov/browse/{}'
    transition_id_for_ready = '11'
    transition_id_for_start_progress = '21'

    def __init__(self, title: str, description: str, in_progress: bool, auth: Auth):
        self.title = title
        self.description = description
        self.id = None
        self.url = None
        self.auth = auth
        self.in_progress = in_progress

    def create(self):
        self._create()

        if self.in_progress:
            self._transition(self.transition_id_for_ready)
            self._transition(self.transition_id_for_start_progress)

        return self.id, self.url

    def _create(self):
        json = {
            'fields': {
                'project': {
                    'key': 'QPPFC'
                },
                'summary': self.title,
                'description': self.description,
                'issuetype': {
                    'name': 'Triage Task'
                },
                'components': [{
                    'name': 'Foundational'
                }]
            }
        }

        response = requests.post(self.api_url, json=json,
                                 auth=HTTPBasicAuth(self.auth.username(), self.auth.password()))
        response.raise_for_status()

        response_json = response.json()

        self.id = response_json['key']
        self.url = self.base_url.format(self.id)

    def _transition(self, id_of_transition):
        json = {
            'transition': {
                'id': id_of_transition
            }
        }

        response = requests.post(self.api_url + self.id + '/transitions', json=json,
                                 auth=HTTPBasicAuth(self.auth.username(), self.auth.password()))
        response.raise_for_status()
