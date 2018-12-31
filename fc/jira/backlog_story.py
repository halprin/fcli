from . backlog_issue import BacklogIssue
from ..auth.auth import Auth
import requests
from requests.auth import HTTPBasicAuth
from ..exceptions.task_exception import TaskException


class BacklogStory(BacklogIssue):

    def __init__(self):
        self.duration = None
        self.cost_of_delay = None

    @classmethod
    def from_json(cls, json: dict, auth: Auth):
        new_story = cls()
        super(BacklogStory, new_story).from_json(json, auth)

        return new_story

    @classmethod
    def from_args(cls, title: str, description: str, auth: Auth):
        new_story = cls()
        super(BacklogStory, new_story).from_args(title, description, auth)

        return new_story

    def type_str(self) -> str:
        return 'Story'

    def set_duration(self, dur: str):
        self.duration = dur

    def set_cost_of_delay(self, cod: str):
        self.cost_of_delay = cod

    def _extra_json_for_create(self, existing_json: dict):
        pass

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
