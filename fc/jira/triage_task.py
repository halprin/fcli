from .task import Task
from datetime import datetime
from ..auth.auth import Auth
import requests
from requests.auth import HTTPBasicAuth


class TriageTask(Task):

    # Triage workflow
    # Triage -> Ready (11)
    # Ready -> In Progress (21)
    # In Progress -> Closed (31)
    # In Progress -> Ready (61)
    # In Progress -> Blocked (71)
    # Blocked -> In Progress (81)
    # Closed -> Triage (41)
    # Closed -> In Progress (51)
    transition_dict = {
        'Ready': {
            'Triage': [21, 31, 41],
            'In Progress': [21],
            'Closed': [21, 31],
            'Blocked': [21, 71]},
        'In Progress': {
            'Triage': [31, 41],
            'Ready': [61],
            'Closed': [31],
            'Blocked': [71]},
        'Blocked': {
            'Triage': [81, 31, 41],
            'Ready': [81, 61],
            'In Progress': [81],
            'Closed': [81, 31]},
        'Closed': {
            'Triage': [41],
            'Ready': [51, 61],
            'In Progress': [51],
            'Blocked': [51, 71]},
        'Triage': {
            'Ready': [11],
            'In Progress': [11, 21],
            'Closed': [11, 21, 31],
            'Blocked': [11, 21, 71]}
    }

    importance_to_score = {
        'High': 10,
        'high': 10,
        'Medium': 5,
        'medium': 5,
        'Low': 1,
        'low': 1
    }

    loe_to_score = {
        'High': 1,
        'high': 1,
        'Medium': 5,
        'medium': 5,
        'Low': 10,
        'low': 10
    }

    date_to_score = {
        (0, 7): 20,
        (8, 14): 15,
        (15, 28): 10,
        (29, 42): 5
    }

    @classmethod
    def from_json(cls, json: dict, auth: Auth):
        new_task = cls()
        super(TriageTask, new_task).from_json(json, auth)

        new_task.importance = json['fields']['customfield_19904']['value']\
            if json['fields']['customfield_19904'] is not None else None
        new_task.level_of_effort = json['fields']['customfield_13405']['value']\
            if json['fields']['customfield_13405'] is not None else None
        new_task.due_date = datetime.strptime(json['fields']['customfield_19905'], '%Y-%m-%d')\
            if json['fields']['customfield_19905'] is not None else None

        return new_task

    @classmethod
    def from_args(cls, title: str, description: str, in_progress: bool, no_assign: bool, importance: str,
                  level_of_effort: str, due_date: datetime, auth: Auth):
        new_task = cls()
        super(TriageTask, new_task).from_args(title, description, auth)

        new_task.in_progress = in_progress
        new_task.no_assign = no_assign
        new_task.importance = importance
        new_task.level_of_effort = level_of_effort
        new_task.due_date = due_date

        return new_task

    def create(self):
        super(TriageTask, self).create()

        self.score()

        if self.in_progress:
            self._transition(self.transition_id_for_triage_ready)
            self._transition(self.transition_id_for_start_progress)

        return self.id, self.url

    def type_str(self) -> str:
        return 'Triage'

    def score(self) -> int:
        score = self._calculate_score()
        self._update_triage_vfr(score)
        return score

    def _calculate_score(self) -> int:

        importance_score = self._importance_score()
        loe_score = self._loe_score()
        date_score = self._date_score()

        return importance_score + loe_score + date_score

    def _importance_score(self) -> int:
        return self.importance_to_score.get(self.importance, 0)

    def _loe_score(self) -> int:
        return self.loe_to_score.get(self.level_of_effort, 0)

    def _date_score(self) -> int:
        if self.due_date is not None:
            try:

                today = datetime.today()

                day_diff = (self.due_date - today).days

                date_score = self._date_score_from_day_delta(day_diff)

            except (ValueError, TypeError) as exception:
                date_score = 0
        else:
            date_score = 0

        return date_score

    def _date_score_from_day_delta(self, days_delta: int) -> int:

        if days_delta < 0:
            return 20 + (days_delta * -5)
        else:
            for key in self.date_to_score:
                if key[0] <= days_delta <= key[1]:
                    return self.date_to_score[key]

        return 0

    def _update_triage_vfr(self, score: int):
        json = {
            'fields': {
                'customfield_18402': score
            }
        }

        # custom field for VFR = customfield_18402

        response = requests.put(self.api_url + self.id, json=json,
                                auth=HTTPBasicAuth(self.auth.username(), self.auth.password()))
        response.raise_for_status()

    def _extra_json_for_create(self, existing_json: dict):
        existing_json['fields']['issuetype'] = {
            'name': 'Triage Task'
        }

        # importance
        existing_json['fields']['customfield_19904'] = {
            'value': self.importance
        }

        # loe
        existing_json['fields']['customfield_13405'] = {
            'value': self.level_of_effort
        }

        # due date/date needed
        existing_json['fields']['customfield_19905'] = self.due_date.strftime('%Y-%m-%d')

        if not self.no_assign:
            existing_json['fields']['assignee'] = {
                'name': self.auth.username()
            }

    def _get_transition_dict(self) -> dict:
        return self.transition_dict
