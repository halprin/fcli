import click
from ..jira.task import Task
from requests.exceptions import HTTPError
from ..auth.fileauth import FileAuth
from ..auth.keyboardauth import KeyboardAuth


@click.group()
def cli():
    pass


@cli.command()
@click.argument('title')
@click.argument('description')
@click.option('--username')
def task(title, description, username):
    click.echo('Adding triage task {}; {}'.format(title, description))

    auth = None
    if username is None:
        auth = FileAuth()
    else:
        auth = KeyboardAuth(username=username)

    new_task = Task(title, description, auth)
    try:
        task_id, url = new_task.create()
        click.echo('Triage task {} added at {}'.format(task_id, url))
    except HTTPError as exception:
        click.echo('Triage task creation failed with {}'.format(exception))
