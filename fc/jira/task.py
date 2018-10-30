import requests
from requests.auth import HTTPBasicAuth
from ..auth.auth import Auth
from typing import Optional


class Task:
    api_url = 'https://jira.cms.gov/rest/api/2/issue/'
    base_url = 'https://jira.cms.gov/browse/{}'
    transition_id_for_triage_ready = '11'
    transition_id_for_start_progress = '21'
    transition_id_for_ready_for_refinement = '201'
    transition_id_for_refined = '211'
    transition_id_for_task_ready = '221'
    issue_assigned_sprint_field = 'customfield_10005'

    def __init__(self, title: str, description: str, auth: Auth):
        self.title = title
        self.description = description
        self.id = None
        self.url = None
        self.auth = auth

    def create(self):
        json = {
            'fields': {
                'project': {
                    'key': 'QPPFC'
                },
                'summary': self.title,
                'description': self.description,
                'components': [{
                    'name': 'Foundational'
                }]
            }
        }

        self._extra_json_for_create(json)

        response = requests.post(self.api_url, json=json,
                                 auth=HTTPBasicAuth(self.auth.username(), self.auth.password()))
        response.raise_for_status()

        response_json = response.json()

        self.id = response_json['key']
        self.url = self.base_url.format(self.id)

        return self.id, self.url

    def _extra_json_for_create(self, existing_json: dict):
        raise NotImplementedError

    def type_str(self) -> str:
        raise NotImplementedError

    def _transition(self, id_of_transition: str):
        json = {
            'transition': {
                'id': id_of_transition
            }
        }

        response = requests.post(self.api_url + self.id + '/transitions', json=json,
                                 auth=HTTPBasicAuth(self.auth.username(), self.auth.password()))
        response.raise_for_status()

    def _get_issue(self, issue_id: str) -> dict:
        response = requests.get(self.api_url + issue_id,
                                auth=HTTPBasicAuth(self.auth.username(), self.auth.password()))
        response.raise_for_status()

        return response.json()

    def _get_active_sprint_id_of_issue(self, issue_id: str) -> Optional[int]:
        issue = self._get_issue(issue_id)

        sprint_list = issue['fields'][self.issue_assigned_sprint_field]

        if sprint_list is None:
            return None

        active_sprint = sprint_list[-1]
        id_begin_token = 'id='
        id_begin = active_sprint.find(id_begin_token) + len(id_begin_token)
        id_end = active_sprint.find(',', id_begin)

        return int(active_sprint[id_begin:id_end])
