import click
import json
from ..jira.triage_task import TriageTask
from ..jira import tasks
from requests.exceptions import HTTPError
from ..auth.combo import ComboAuth
import click_datetime
from . import cli_library


@click.group()
def triage():
    pass


@triage.command()
@click.argument('title')
@click.argument('description')
@click.option('--username')
@click.option('--in-progress', is_flag=True)
@click.option('--assign', is_flag=True)
@click.option('--importance', prompt=True, type=click.Choice(['Low', 'Medium', 'High'], case_sensitive=False))
@click.option('--effort', prompt='Level of Effort', type=click.Choice(['Low', 'Medium', 'High'], case_sensitive=False))
@click.option('--due', prompt='Due date (mm/dd/yyyy)', type=click_datetime.Datetime(format='%m/%d/%Y'))
def create(title, description, username, in_progress, assign, importance, effort, due):
    cli_library.echo('Adding triage task {}; {}'.format(title, description))

    auth = ComboAuth(username)

    new_task = TriageTask.from_args(title, description, in_progress, assign, importance, effort, due, auth)
    try:
        task_id, url = new_task.create()
        cli_library.echo('Triage task {} added at {}'.format(task_id, url))
        if in_progress:
            cli_library.echo('Triage task put into In Progress')
    except HTTPError as exception:
        cli_library.fail_execution(1, 'Triage task creation failed with {}'.format(exception))


@triage.command()
@click.option('--username')
def search(username):
    cli_library.echo('Searching for triage tasks')

    auth = ComboAuth(username)

    try:
        triage_tasks_raw = tasks.search_for_triage(auth)
        cli_library.echo('Triage tasks: {}'.format(json.dumps(triage_tasks_raw, indent=4)))
    except HTTPError as exception:
        cli_library.fail_execution(1, 'Task search failed with {}'.format(exception))
