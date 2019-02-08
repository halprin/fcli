from . backlog_issue import BacklogIssue
from ..auth.auth import Auth
import requests
from requests.auth import HTTPBasicAuth
from ..exceptions.task_exception import TaskException


class BacklogStory(BacklogIssue):

    def __init__(self):
        self.duration = None
        self.cost_of_delay = None
        self.ac = None

    @classmethod
    def from_json(cls, json: dict, auth: Auth):
        new_task = super(BacklogStory, cls).from_json(json, auth)

        new_task.ac = json['fields']['customfield_14219']

        issue_links = json['fields']['issuelinks']

        for issue_link in issue_links:
            if issue_link['type']['id'] == '10603':
                new_task.parent_story = issue_link['outwardIssue']['key']
                break

        return new_task

    @classmethod
    def from_args(cls, title: str, description: str, ac: str, auth: Auth):
        new_task = super(BacklogStory, cls).from_args(title, description, auth)

        new_task.ac = ac

        return new_task

    def type_str(self) -> str:
        return 'Story'

    def set_duration(self, dur: str):
        self.duration = dur

    def set_cost_of_delay(self, cod: str):
        self.cost_of_delay = cod

    def _extra_json_for_create(self, existing_json: dict):

        existing_json['fields']['issuetype'] = {
            'name': 'Story'
        }

        # fill in for the ac field
        existing_json['fields']['customfield_14219'] = self.ac

    def score(self) -> float:

        if self.type != 'Story':
            raise TaskException('Invalid type: Can only add VFR to Story types')

        vfr_value = round(self.cost_of_delay / self.duration, 2)

        # store vfr, duration, cost of delay
        json = {
            'fields': {
                'customfield_18402': vfr_value,
                'customfield_18400': self.duration,
                'customfield_18401': self.cost_of_delay
            }
        }

        response = requests.put(self.api_url + self.id, json=json,
                                auth=HTTPBasicAuth(self.auth.username(), self.auth.password()))
        response.raise_for_status()

        # transition to Refined
        self.transition('Refined')

        return vfr_value
