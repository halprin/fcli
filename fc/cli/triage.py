import click
import json
from ..jira.triage_task import TriageTask
from ..jira import tasks
from requests.exceptions import HTTPError
from ..auth.combo import ComboAuth
import click_datetime


@click.group()
def triage():
    pass


@triage.command()
@click.argument('title')
@click.argument('description')
@click.option('--username')
@click.option('--in-progress', is_flag=True)
@click.option('--no-assign', is_flag=True)
@click.option('--importance', prompt=True, type=click.Choice(['Low', 'Medium', 'High'], case_sensitive=False))
@click.option('--effort', prompt='Level of Effort', type=click.Choice(['Low', 'Medium', 'High'], case_sensitive=False))
@click.option('--due', prompt='Due date (mm/dd/yyyy)', type=click_datetime.Datetime(format='%m/%d/%Y'))
def create(title, description, username, in_progress, no_assign, importance, effort, due):
    click.echo('Adding triage task {}; {}'.format(title, description))

    auth = ComboAuth(username)

    new_task = TriageTask(title, description, in_progress, no_assign, importance, effort, due, auth)
    try:
        task_id, url = new_task.create()
        click.echo('Triage task {} added at {}'.format(task_id, url))
        if in_progress:
            click.echo('Triage task put into In Progress')
    except HTTPError as exception:
        click.echo('Triage task creation failed with {}'.format(exception))


@triage.command()
@click.option('--username')
def search(username):
    click.echo('Searching for triage tasks')

    auth = ComboAuth(username)

    try:
        triage_tasks = tasks.triage_search(auth)
        click.echo('Triage tasks: {}'.format(json.dumps(triage_tasks, indent=4)))
    except HTTPError as exception:
        click.echo('Task search failed with {}'.format(exception))


@triage.command()
@click.option('--username')
def score(username):
    click.echo('Scoring triage tasks')

    auth = ComboAuth(username)

    try:
        triage_tasks = tasks.triage_search(auth)
        for task in triage_tasks['issues']:
            click.echo('Generating score for task {}'.format(task['key']))
            score = tasks.score(task, auth)
            click.echo('Triage task VFR updated with {} for {}'.format(score, task['key']))
    except HTTPError as exception:
        click.echo('Task search failed with {}'.format(exception))
