import requests
from requests import HTTPError
from requests.auth import HTTPBasicAuth
from ..exceptions.task_exception import TaskException
from .issue import Issue
from ..auth.auth import Auth
from typing import Tuple


class FcIssue(Issue):

    score_jira_field = 'customfield_18402'
    closed_states = ['Resolved', 'Closed']

    def __init__(self):
        self.score_value = None

    @classmethod
    def from_json(cls, json: dict, auth: Auth):
        new_issue = super(FcIssue, cls).from_json(json, auth)

        new_issue.score_value = json[cls.fields_jira_field][cls.score_jira_field]

        return new_issue

    def transition(self, state: str, resolution: str = None, comment: str = None):

        if state != self.state:

            # use created Task (could be Backlog task or Triage task) to transition to desired state
            # Look up starting state in dictionary
            # then look up task type (Backlog or Triage)
            # then look up end state
            # array is the sequence of state transitions in order to iterate through

            transition_dict = self._get_transition_dict()

            try:
                transition_arr = transition_dict[self.state][state]
            except (KeyError, TypeError) as exception:
                raise TaskException('Invalid states for task type: {}, {} : error {}'.
                                    format(self.state, state, exception))

            if transition_arr is None:
                raise TaskException('Unable to find a transition path from {} to {}'.format(self.state, state))
            else:
                try:
                    for transition_id in transition_arr:
                        self._transition(transition_id, resolution, comment)

                except HTTPError as exception:
                    raise TaskException('Failure to complete transition path: {}'.format(exception))

    def _transition(self, id_of_transition: int, resolution: str = None, comment: str = None):

        # we don't do anything special with the resolution when re-opening an issue
        # the jira api does NOT support unsetting the resolution field
        # a post function needs to be attached to the transition through the jira UI

        json = {
            'transition': {
                'id': str(id_of_transition)
            }
        }

        if resolution is not None:
            json['fields'] = {
                'resolution': {
                    'name': resolution
                }
            }

        if comment is not None:
            json['update'] = {
                'comment': [
                    {
                        'add': {
                            'body': comment
                        }
                    }
                ]
            }

        response = requests.post(self.api_url + self.id + '/transitions', json=json,
                                 auth=HTTPBasicAuth(self.auth.username(), self.auth.password()))
        response.raise_for_status()

    def _get_transition_dict(self) -> dict:
        raise NotImplementedError

    def score(self) -> Tuple:
        raise NotImplementedError

    def type_str(self) -> str:
        return 'FcIssue'
