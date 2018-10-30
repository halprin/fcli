from .task import Task
from ..auth.auth import Auth


class BacklogTask(Task):
    def __init__(self, title: str, description: str, parent_story: str, auth: Auth):
        super(BacklogTask, self).__init__(title, description, auth)

        self.parent_story = parent_story

        self.title = self.parent_story + ': ' + self.title

    def create(self):
        super(BacklogTask, self).create()

        self._transition(self.transition_id_for_ready_for_refinement)
        self._transition(self.transition_id_for_refined)
        self._transition(self.transition_id_for_task_ready)

        return self.id, self.url

    def type_str(self) -> str:
        return 'Backlog'

    def _extra_json_for_create(self, existing_json: dict):
        existing_json['fields']['issuetype'] = {
            'name': 'Task'
        }

        existing_json['update'] = {
            'issuelinks': [{
                'add': {
                    'type': {
                        'name': 'Implements',
                        'inward': 'is implemented by',
                        'outward': 'implements'
                    },
                    'outwardIssue': {
                        'key': self.parent_story
                    }
                }
            }]
        }

        parent_story_sprint = self._get_active_sprint_id_of_issue(self.parent_story)
        if parent_story_sprint is not None:
            existing_json['fields'][self.issue_assigned_sprint_field] = parent_story_sprint
