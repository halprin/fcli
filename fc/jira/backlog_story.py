from . backlog_issue import BacklogIssue
from ..auth.auth import Auth
import requests
from requests.auth import HTTPBasicAuth
from ..exceptions.task_exception import TaskException


class BacklogStory(BacklogIssue):
    _acceptance_criteria_jira_field = 'customfield_14219'
    _story_type_str = 'Story'

    def __init__(self):
        self.duration = None
        self.cost_of_delay = None
        self.acceptance_criteria = None

    @classmethod
    def from_json(cls, json: dict, auth: Auth):
        new_story = super(BacklogStory, cls).from_json(json, auth)

        new_story.acceptance_criteria = json[cls.fields_jira_field][cls._acceptance_criteria_jira_field]

        return new_story

    @classmethod
    def from_args(cls, title: str, description: str, acceptance_criteria: str, auth: Auth):
        new_story = super(BacklogStory, cls).from_args(title, description, auth)

        new_story.acceptance_criteria = acceptance_criteria

        return new_story

    def type_str(self) -> str:
        return self._story_type_str

    def set_duration(self, dur: str):
        self.duration = dur

    def set_cost_of_delay(self, cod: str):
        self.cost_of_delay = cod

    def _extra_json_for_create(self, existing_json: dict):

        existing_json[self.fields_jira_field][self.issuetype_jira_field] = {
            self.name_jira_field: self._story_type_str
        }

        # fill in for the ac field
        existing_json[self.fields_jira_field][self._acceptance_criteria_jira_field] = self.acceptance_criteria

    def score(self) -> float:

        if self.type != self._story_type_str:
            raise TaskException('Invalid type: Can only add VFR to Story types')

        vfr_value = round(self.cost_of_delay / self.duration, 2)

        # store vfr, duration, cost of delay
        json = {
            self.fields_jira_field: {
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
