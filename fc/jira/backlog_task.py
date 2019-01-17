from . backlog_issue import BacklogIssue
from ..auth.auth import Auth


class BacklogTask(BacklogIssue):

    @classmethod
    def from_json(cls, json: dict, auth: Auth):
        new_task = super(BacklogTask, cls).from_json(json, auth)

        issue_links = json['fields']['issuelinks']

        for issue_link in issue_links:
            if issue_link['type']['id'] == '10603':
                new_task.parent_story = issue_link['outwardIssue']['key']
                break

        return new_task

    @classmethod
    def from_args(cls, title: str, description: str, parent_story: str, auth: Auth):
        new_task = super(BacklogTask, cls).from_args(title, description, auth)

        new_task.parent_story = parent_story

        new_task.title = new_task.parent_story + ': ' + new_task.title

        return new_task

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

    def _get_transition_dict(self) -> dict:
        return self.transition_dict
