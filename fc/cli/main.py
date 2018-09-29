import click
from ..jira.task import Task
from requests.exceptions import HTTPError


@click.group()
def cli():
    pass


@cli.command()
@click.argument('title')
@click.argument('description')
def task(title, description):
    click.echo('Adding triage task {}; {}'.format(title, description))

    new_task = Task(title, description)
    try:
        task_id, url = new_task.create()
        click.echo('Triage task {} added at {}'.format(task_id, url))
    except HTTPError as exception:
        click.echo('Triage task creation failed with {}'.format(exception))
