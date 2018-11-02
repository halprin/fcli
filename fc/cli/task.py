import click
import json
from ..jira.triage_task import TriageTask
from ..jira import tasks
from requests.exceptions import HTTPError
from ..auth.combo import ComboAuth
import click_datetime


@click.group()
def task():
    pass


@task.command()
@click.option('--username')
@click.argument('task_id')
@click.argument('state')
def move(username: str, task_id: str, state: str):
    click.echo('Transitioning task')

    auth = ComboAuth(username)

    try:
        # use a factory method to GET the issue by key
        # use created Task (could be backlog task or triage task) to transition to desired state



    except HTTPError as exception:
        click.echo('Task search failed with {}'.format(exception))
