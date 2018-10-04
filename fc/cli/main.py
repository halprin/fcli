import click
from ..jira.task import Task
from requests.exceptions import HTTPError
from ..auth.combo import ComboAuth


@click.group()
def cli():
    pass


@cli.command()
@click.argument('title')
@click.argument('description')
@click.option('--username')
@click.option('--in-progress', is_flag=True)
def task(title, description, username, in_progress):
    click.echo('Adding triage task {}; {}'.format(title, description))

    auth = ComboAuth(username)

    new_task = Task(title, description, in_progress, auth)
    try:
        task_id, url = new_task.create()
        click.echo('Triage task {} added at {}'.format(task_id, url))
        if in_progress:
            click.echo('Triage task put into In Progress')
    except HTTPError as exception:
        click.echo('Triage task creation failed with {}'.format(exception))
