import requests
from requests.auth import HTTPBasicAuth

from fc.jira import tasks
from ..auth.auth import Auth
from typing import Optional
from datetime import datetime


class Task:
    api_url = 'https://jira.cms.gov/rest/api/2/issue/'
    base_url = 'https://jira.cms.gov/browse/{}'
    transition_id_for_triage_ready = '11'
    transition_id_for_start_progress = '21'
    transition_id_for_ready_for_refinement = '201'
    transition_id_for_refined = '211'
    transition_id_for_task_ready = '221'
    issue_assigned_sprint_field = 'customfield_10005'

    def __init__(self, params: dict, auth: Auth):
        self.title = params.get('title')
        self.description = params.get('description')
        self.id = params.get('id')
        self.url = params.get('url')
        self.type = params.get('type')
        self.state = params.get('state')
        self.auth = auth

    # def __init__(self, json: dict, auth: Auth):
    #     self.title = json['fields']['summary']
    #     self.description = json['fields']['description']
    #     self.id = json['key']
    #     self.url = self.base_url.format(self.id)
    #     self.type = json['fields']['issuetype']['name']
    #     self.state = json['fields']['status']['name']
    #     self.auth = auth

    # def __init__(self, title: str, description: str, auth: Auth):
    #     self.title = title
    #     self.description = description
    #     self.id = None
    #     self.url = None
    #     self.type = None
    #     self.state = None
    #     self.auth = auth

    @classmethod
    def from_json(cls, json: dict, auth: Auth):
        tmp_dict = {
            'title': json['fields']['summary'],
            'description': json['fields']['description'],
            'id': json['key'],
            'url': cls.base_url.format(json['key']),
            'type': json['fields']['issuetype']['name'],
            'state': json['fields']['status']['name']
        }

        return cls(tmp_dict, auth)

    @classmethod
    def from_args(cls, title: str, description: str, auth: Auth):
        tmp_dict = {
            'title': title,
            'description': description
        }

        return cls(tmp_dict, auth)

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

    def _get_active_sprint_id_of_issue(self, issue_id: str) -> Optional[int]:
        issue = tasks.get_issue(self.api_url, issue_id, self.auth)

        sprint_list = issue['fields'][self.issue_assigned_sprint_field]

        if sprint_list is None:
            return None

        active_sprint = sprint_list[-1]
        id_begin_token = 'id='
        id_begin = active_sprint.find(id_begin_token) + len(id_begin_token)
        id_end = active_sprint.find(',', id_begin)

        return int(active_sprint[id_begin:id_end])

    def _modify_description_for_parameters(self, importance: str, level_of_importance: str, due_date: datetime):
        raise NotImplementedError
