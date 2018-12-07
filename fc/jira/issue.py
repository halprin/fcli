import requests
from requests import HTTPError
from requests.auth import HTTPBasicAuth
from ..auth.auth import Auth
from typing import Optional
from ..exceptions.task_exception import TaskException


class Issue:
    api_url = 'https://jira.cms.gov/rest/api/2/issue/'
    base_url = 'https://jira.cms.gov/browse/{}'
    transition_id_for_triage_ready = '11'
    transition_id_for_start_progress = '21'
    transition_id_for_ready_for_refinement = '201'
    transition_id_for_refined = '211'
    transition_id_for_task_ready = '221'
    issue_assigned_sprint_field = 'customfield_10005'

    def __init__(self):
        self.title = None
        self.description = None
        self.id = None
        self.url = None
        self.type = None
        self.state = None
        self.auth = None

    def from_json(self, json: dict, auth: Auth):
        self.title = json['fields']['summary']
        self.description = json['fields']['description']
        self.id = json['key']
        self.url = self.base_url.format(json['key'])
        self.type = json['fields']['issuetype']['name']
        self.state = json['fields']['status']['name']
        self.auth = auth

        return self

    def from_args(self, title: str, description: str, auth: Auth):
        self.title = title
        self.description = description
        self.auth = auth

        return self

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

    @classmethod
    def _get_issue(cls, issue_id: str, auth: Auth) -> dict:
        response = requests.get(cls.api_url + issue_id,
                                auth=HTTPBasicAuth(auth.username(), auth.password()))
        response.raise_for_status()

        return response.json()

    def _get_active_sprint_id_of_issue(self, issue_id: str) -> Optional[int]:
        issue = self._get_issue(issue_id, self.auth)

        sprint_list = issue['fields'][self.issue_assigned_sprint_field]

        if sprint_list is None:
            return None

        active_sprint = sprint_list[-1]
        id_begin_token = 'id='
        id_begin = active_sprint.find(id_begin_token) + len(id_begin_token)
        id_end = active_sprint.find(',', id_begin)

        return int(active_sprint[id_begin:id_end])

    @classmethod
    def get_issue(cls, issue_id: str, auth: Auth) -> 'Issue':
        from .backlog_task import BacklogTask
        from .triage_task import TriageTask
        from .el_task import ElTask

        issue_json = {}
        issue = None

        try:
            issue_json = cls._get_issue(issue_id, auth)
        except HTTPError as exception:
            raise TaskException('Invalid issue key {}'.format(issue_id)) from exception

        type = issue_json['fields']['issuetype']['name']
        if type != 'Task' and type != 'Triage Task':
            issue = cls()
            issue.from_json(issue_json, auth)
        elif type == 'Task':
            issue = BacklogTask.from_json(issue_json, auth)
        else:
            labels: list = issue_json['fields']['labels']
            if 'EL' in labels:
                issue = ElTask.from_json(issue_json, auth)
            else:
                issue = TriageTask.from_json(issue_json, auth)

        return issue

    def comment(self, note: str):

        json = { 'body': note }

        response = requests.post('{}{}/comment'.format(self.api_url, self.id), json=json,
                                 auth=HTTPBasicAuth(self.auth.username(), self.auth.password()))
        response.raise_for_status()
