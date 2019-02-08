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
    fields_jira_field = 'fields'
    key_jira_field = 'key'
    name_jira_field = 'name'
    issuetype_jira_field = 'issuetype'
    summary_jira_field = 'summary'
    description_jira_field = 'description'
    project_jira_field = 'project'

    def __init__(self):
        self.title = None
        self.description = None
        self.id = None
        self.url = None
        self.type = None
        self.state = None
        self.auth = None
        self.project = None

    @classmethod
    def from_json(cls, json: dict, auth: Auth):
        new_issue = cls()
        new_issue.title = json[cls.fields_jira_field][cls.summary_jira_field]
        new_issue.description = json[cls.fields_jira_field][cls.description_jira_field]
        new_issue.id = json[cls.key_jira_field]
        new_issue.url = new_issue.base_url.format(json[cls.key_jira_field])
        new_issue.type = json[cls.fields_jira_field][cls.issuetype_jira_field][cls.name_jira_field]
        new_issue.state = json[cls.fields_jira_field]['status'][cls.name_jira_field]
        new_issue.auth = auth
        new_issue.project = json[cls.fields_jira_field][cls.project_jira_field][cls.key_jira_field]

        return new_issue

    @classmethod
    def from_args(cls, title: str, description: str, auth: Auth):
        new_issue = cls()
        new_issue.title = title
        new_issue.description = description
        new_issue.auth = auth

        return new_issue

    def create(self):
        json = {
            self.fields_jira_field: {
                self.project_jira_field: {
                    self.key_jira_field: 'QPPFC'
                },
                self.summary_jira_field: self.title,
                self.description_jira_field: self.description,
                'components': [{
                    self.name_jira_field: 'Foundational'
                }]
            }
        }

        self._extra_json_for_create(json)

        response = requests.post(self.api_url, json=json,
                                 auth=HTTPBasicAuth(self.auth.username(), self.auth.password()))
        response.raise_for_status()

        response_json = response.json()

        self.id = response_json[self.key_jira_field]
        self.url = self.base_url.format(self.id)

        return self.id, self.url

    def _extra_json_for_create(self, existing_json: dict):
        raise NotImplementedError

    def type_str(self) -> str:
        return 'Generic Issue'

    @classmethod
    def _get_issue(cls, issue_id: str, auth: Auth) -> dict:
        response = requests.get(cls.api_url + issue_id,
                                auth=HTTPBasicAuth(auth.username(), auth.password()))
        response.raise_for_status()

        return response.json()

    def _get_active_sprint_id_of_issue(self, issue_id: str) -> Optional[int]:
        issue = self._get_issue(issue_id, self.auth)

        sprint_list = issue[self.fields_jira_field][self.issue_assigned_sprint_field]

        if sprint_list is None:
            return None

        active_sprint = sprint_list[-1]
        id_begin_token = 'id='
        id_begin = active_sprint.find(id_begin_token) + len(id_begin_token)
        id_end = active_sprint.find(',', id_begin)

        return int(active_sprint[id_begin:id_end])

    @classmethod
    def get_issue(cls, issue_id: str, auth: Auth) -> 'Issue':
        from .backlog_story import BacklogStory
        from .backlog_task import BacklogTask
        from .triage_task import TriageTask
        from .el_task import ElTask

        issue_json = {}
        issue = None

        try:
            issue_json = cls._get_issue(issue_id, auth)
        except HTTPError as exception:
            raise TaskException('Invalid issue key {}'.format(issue_id)) from exception

        project = issue_json[cls.fields_jira_field][cls.project_jira_field][cls.key_jira_field]
        issue_type = issue_json[cls.fields_jira_field][cls.issuetype_jira_field][cls.name_jira_field]
        if project != 'QPPFC':
            issue = cls.from_json(issue_json, auth)
        elif issue_type == 'Story':
            issue = BacklogStory.from_json(issue_json, auth)
        elif issue_type == 'Task':
            issue = BacklogTask.from_json(issue_json, auth)
        elif issue_type == 'Triage Task':
            labels: list = issue_json[cls.fields_jira_field]['labels']
            if 'EL' in labels:
                issue = ElTask.from_json(issue_json, auth)
            else:
                issue = TriageTask.from_json(issue_json, auth)
        else:
            issue = cls.from_json(issue_json, auth)

        return issue

    def comment(self, note: str):

        json = {
            'body': note
        }

        response = requests.post('{}{}/comment'.format(self.api_url, self.id), json=json,
                                 auth=HTTPBasicAuth(self.auth.username(), self.auth.password()))
        response.raise_for_status()
