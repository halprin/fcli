import requests
from requests import HTTPError
from requests.auth import HTTPBasicAuth
from ..auth.auth import Auth
from typing import Optional
from ..exceptions.task_exception import TaskException


class Task:
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
        new_json = {
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

        self._extra_json_for_create(new_json)

        response = requests.post(self.api_url, json=new_json,
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

    def transition(self, state: str):

        # use created Task (could be Backlog task or Triage task) to transition to desired state
        # Look up starting state in dictionary
        # then look up task type (Backlog or Triage)
        # then look up end state
        # array is the sequence of state transitions in order to iterate through

        transition_dict = self._get_transition_dict()

        try:
            transition_arr = transition_dict[self.state][state]
        except (KeyError, TypeError) as exception:
            raise TaskException('Invalid states for task type: {}, {} : error {}'.format(self.state, state, exception))

        if transition_arr is None:
            raise TaskException('Unable to find a transition path from {} to {}'.format(self.state, state))
        else:
            try:
                for transition_id in transition_arr:
                    self._transition(transition_id)

            except HTTPError as exception:
                raise TaskException('Failure to complete transition path: {}'.format(exception))

    def _transition(self, id_of_transition: int):

        json = {
            'transition': {
                'id': id_of_transition
            }
        }

        response = requests.post(self.api_url + self.id + '/transitions', json=json,
                                 auth=HTTPBasicAuth(self.auth.username(), self.auth.password()))
        response.raise_for_status()

    @classmethod
    def get_task(cls, issue_id: str, auth: Auth) -> 'Task':
        from .backlog_task import BacklogTask
        from .triage_task import TriageTask
        from .el_task import ElTask

        issue_json = {}
        task = None

        try:
            issue_json = cls._get_issue(issue_id, auth)
        except HTTPError as exception:
            raise TaskException('Invalid issue key {}'.format(issue_id)) from exception

        type = issue_json['fields']['issuetype']['name']
        if type != 'Task' and type != 'Triage Task':
            raise TaskException('Invalid issue type {}'.format(type))
        elif type == 'Task':
            task = BacklogTask.from_json(issue_json, auth)
        else:
            labels: list = issue_json['fields']['labels']
            if 'EL' in labels:
                task = ElTask.from_json(issue_json, auth)
            else:
                task = TriageTask.from_json(issue_json, auth)

        return task

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

    def _get_transition_dict(self) -> dict:
        raise NotImplementedError
