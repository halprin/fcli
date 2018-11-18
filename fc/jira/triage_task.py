from . import task
from datetime import datetime
from ..auth.auth import Auth
import re
from typing import Tuple, Optional
import requests
from requests.auth import HTTPBasicAuth


class TriageTask(task.Task):

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

    importance_dict = {
        'High': 10,
        'high': 10,
        'Medium': 5,
        'medium': 5,
        'Low': 1,
        'low': 1
    }

    loe_dict = {
        'High': 1,
        'high': 1,
        'Medium': 5,
        'medium': 5,
        'Low': 10,
        'low': 10
    }

    date_dict = {
        (0, 7): 20,
        (8, 14): 15,
        (15, 28): 10,
        (29, 42): 5
    }

    @classmethod
    def from_json(cls, json: dict, auth: Auth):
        new_task = cls()
        super(TriageTask, new_task).from_json(json, auth)
        # next 3 instance variables will be populated with next set of changes, for now None
        new_task.importance = None
        new_task.level_of_effort = None
        new_task.due_date = None
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

        new_task._modify_description_for_parameters(new_task.importance, new_task.level_of_effort, new_task.due_date)

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
        (imp_part, loe_part, date_part) = self._find_triage_score_parts()
        score = self._calc_triage_score(imp_part, loe_part, date_part)
        self._update_triage_vfr(score)
        return score

    def _find_triage_score_parts(self) -> Tuple[Optional[str], Optional[str], Optional[str]]:

        if self.importance is not None and self.level_of_effort is not None and self.due_date is not None:
            return self.importance, self.level_of_effort, self.due_date
        else:

            regex = 'Importance: (.*)\\r\\n\\r\\nLOE: (.*)\\r\\n\\r\\nDate [N|n]eeded: (.*)\\r\\n\\r\\n'

            m = re.search(regex, self.description, re.MULTILINE)
            if m is None:
                return None, None, None
            else:
                return m.groups()

    def _calc_triage_score(self, imp_part: str, loe_part: str, date_part: str) -> int:

        dt_score = 0

        imp_score = self.importance_dict.get(imp_part, 0)

        loe_score = self.loe_dict.get(loe_part, 0)

        try:
            dt_obj = datetime.strptime(date_part, '%m/%d/%Y')

            today = datetime.today()

            day_diff = (dt_obj - today).days

            dt_score = self._get_date_score(day_diff)

        except (ValueError, TypeError):
            dt_score = 0

        return imp_score + loe_score + dt_score

    def _update_triage_vfr(self, score: int):
        json = {
            'fields': {
                'customfield_18402': score
            }
        }

        # custom field for VFR = customfield_18402

        response = requests.put(self.api_url + self.id, json=json, auth=HTTPBasicAuth(self.auth.username(), self.auth.password()))
        response.raise_for_status()

    def _get_date_score(self, num_days: int) -> int:

        if num_days < 0:
            return 20 + (num_days * -5)
        else:
            for key in self.date_dict:
                if key[0] <= num_days <= key[1]:
                    return self.date_dict[key]

        return 0

    def _extra_json_for_create(self, existing_json: dict):
        existing_json['fields']['issuetype'] = {
            'name': 'Triage Task'
        }

        if not self.no_assign:
            existing_json['fields']['assignee'] = {
                'name': self.auth.username()
            }

    def _modify_description_for_parameters(self, importance: str, level_of_importance: str, due_date: datetime):
        additional_description = 'Importance: {}\r\n\r\nLOE: {}\r\n\r\nDate needed: {}'\
            .format(importance, level_of_importance, due_date.strftime('%m/%d/%Y'))
        self.description = self.description + '\r\n\r\n' + additional_description + '\r\n\r\n'

    def _get_transition_dict(self) -> dict:
        return self.transition_dict
