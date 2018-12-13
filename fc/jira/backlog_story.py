from . backlog_issue import BacklogIssue
from ..auth.auth import Auth
import requests
from requests.auth import HTTPBasicAuth
from ..exceptions.task_exception import TaskException


class BacklogStory(BacklogIssue):

    @classmethod
    def from_json(cls, json: dict, auth: Auth):
        new_story = cls()
        super(BacklogStory, new_story).from_json(json, auth)

        return new_story

    @classmethod
    def from_args(cls, title: str, description: str, parent_story: str, auth: Auth):
        new_story = cls()
        super(BacklogStory, new_story).from_args(title, description, auth)

        return new_story

    def create(self):
        super(BacklogStory, self).create()

        return self.id, self.url

    def type_str(self) -> str:
        return 'Story'

    def _extra_json_for_create(self, existing_json: dict):
        pass

    def _get_transition_dict(self) -> dict:
        return self.transition_dict

    def update_vfr(self, duration: int, cost_of_delay: int) -> float:

        if self.type != 'Story':
            raise TaskException('Invalid type: Can only add VFR to Story types')

        vfr_value = round(cost_of_delay / duration, 2)

        # store vfr, duration, cost of delay
        json = {
            'fields': {
                'customfield_18402': vfr_value,
                'customfield_18400': duration,
                'customfield_18401': cost_of_delay
            }
        }

        response = requests.put(self.api_url + self.id, json=json,
                                auth=HTTPBasicAuth(self.auth.username(), self.auth.password()))
        response.raise_for_status()

        # transition to Refined
        self.transition('Refined')

        return vfr_value
