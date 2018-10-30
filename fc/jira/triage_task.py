from .task import Task
from datetime import datetime
from ..auth.auth import Auth
from . import tasks


class TriageTask(Task):
    def __init__(self, title: str, description: str, in_progress: bool, no_assign: bool, importance: str,
                 level_of_effort: str, due_date: datetime, auth: Auth):
        super(TriageTask, self).__init__(title, description, auth)

        self.in_progress = in_progress
        self.no_assign = no_assign
        self.importance = importance
        self.level_of_effort = level_of_effort
        self.due_date = due_date

        self._modify_description_for_parameters(self.importance, self.level_of_effort, self.due_date)

    def create(self):
        super(TriageTask, self).create()

        self._update_vfr()

        if self.in_progress:
            self._transition(self.transition_id_for_triage_ready)
            self._transition(self.transition_id_for_start_progress)

        return self.id, self.url

    def type_str(self) -> str:
        return 'Triage'

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

    def _update_vfr(self):
        issue_json = self._get_issue(self.id)
        tasks.score(issue_json, self.auth)
