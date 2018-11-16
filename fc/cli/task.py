import click
from ..jira import tasks
from requests.exceptions import HTTPError
from ..auth.combo import ComboAuth


issue_url = 'https://jira.cms.gov/rest/api/2/issue/'


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

    the_task = None

    try:
        # use a factory method to GET the issue by key
        the_task = tasks.get_task(issue_url, task_id, auth)

    except HTTPError as exception:
        click.echo('Task search failed with {}'.format(exception))

    if the_task is not None:
        the_task.transition(state)
        click.echo('Successfully transitioned {} to state {}'.format(task_id, state))
    else:
        click.echo('Failed to retrieve a task for key {}'.format(task_id))
