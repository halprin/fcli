import requests
from requests import HTTPError
from requests.auth import HTTPBasicAuth
from ..exceptions.task_exception import TaskException
from .issue import Issue


class FcIssue(Issue):
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

    def _get_transition_dict(self) -> dict:
        raise NotImplementedError

    def score(self) -> int:
        raise NotImplementedError

    def type_str(self) -> str:
        return 'FcIssue'
