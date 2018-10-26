import click
import json
from ..jira.task import Task
from ..jira import tasks
from requests.exceptions import HTTPError
from ..auth.combo import ComboAuth

@click.group()
def triage():
    pass

@triage.command()
@click.argument('title')
@click.argument('description')
@click.option('--username')
@click.option('--in-progress', is_flag=True)
@click.option('--no-assign', is_flag=True)
def create(title, description, username, in_progress, no_assign):
    click.echo('Adding task {}; {}'.format(title, description))

    auth = ComboAuth(username)

    new_task = Task(title, description, None, in_progress, no_assign, auth)
    try:
        task_id, url = new_task.create()
        click.echo('{} task {} added at {}'.format(new_task.type_str(), task_id, url))
        if in_progress:
            click.echo('Triage task put into In Progress')
    except HTTPError as exception:
        click.echo('{} task creation failed with {}'.format(new_task.type_str(), exception))

@triage.command()
@click.option('--username')
def search(username):
    click.echo('Searching for triage tasks')

    auth = ComboAuth(username)

    try:
        triage_tasks = tasks.triage_search(auth)
        click.echo('Triage tasks: {}'.format(json.dumps(triage_tasks.json(), indent=4)))
    except HTTPError as exception:
        click.echo('Task search failed with {}'.format(exception))

@triage.command()
@click.option('--username')
def score(username):
    click.echo('Scoring triage tasks')

    auth = ComboAuth(username)

    try:
        triage_tasks = tasks.triage_search(auth)
        for task in triage_tasks.json()['issues']:
            click.echo('Generating score for task {}'.format(task['key']))
            tasks.score(task, auth)
            click.echo('Triage task VFR updated for {}'.format(task['key']))
    except HTTPError as exception:
        click.echo('Task search failed with {}'.format(exception))
