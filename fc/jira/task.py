import requests
from requests.auth import HTTPBasicAuth
from ..auth.auth import Auth


class Task:
    api_url = 'https://jira.cms.gov/rest/api/2/issue/'
    base_url = 'https://jira.cms.gov/browse/{}'
    transition_id_for_triage_ready = '11'
    transition_id_for_start_progress = '21'
    transition_id_for_ready_for_refinement = '201'
    transition_id_for_refined = '211'
    transition_id_for_task_ready = '221'

    def __init__(self, title: str, description: str, parent_story: str, in_progress: bool, auth: Auth):
        self.title = title
        self.description = description
        self.parent_story = parent_story
        self.id = None
        self.url = None
        self.auth = auth
        self.in_progress = in_progress

        if self._is_backlog_task():
            self.title = self.parent_story + ': ' + self.title

    def create(self):
        self._create()

        if self.in_progress and self._is_triage_task():
            self._transition(self.transition_id_for_triage_ready)
            self._transition(self.transition_id_for_start_progress)
        elif self._is_backlog_task():
            self._transition(self.transition_id_for_ready_for_refinement)
            self._transition(self.transition_id_for_refined)
            self._transition(self.transition_id_for_task_ready)

        return self.id, self.url

    def _create(self):
        ticket_type = 'Triage Task' if self._is_triage_task() else 'Task'

        json = {
            'fields': {
                'project': {
                    'key': 'QPPFC'
                },
                'summary': self.title,
                'description': self.description,
                'issuetype': {
                    'name': ticket_type
                },
                'components': [{
                    'name': 'Foundational'
                }]
            }
        }

        if self._is_backlog_task():
            json['update'] = {
                'issuelinks': [{
                    'add': {
                        'type': {
                            'name': 'Implements',
                            'inward': 'is implemented by',
                            'outward': 'implements'
                        },
                        'outwardIssue': {
                            'key': self.parent_story
                        }
                    }
                }]
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

    def _is_triage_task(self):
        return self.parent_story is None

    def _is_backlog_task(self):
        return not self._is_triage_task()
