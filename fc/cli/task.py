import click
from ..jira.task import Task
from requests.exceptions import HTTPError
from ..auth.combo import ComboAuth
from ..jira import tasks
from . import cli_library
from ..exceptions.task_exception import TaskException


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
        the_task = Task.get_issue(task_id, auth)
    except TaskException as exception:
        cli_library.fail_execution(1, 'Task search failed with {}'.format(exception))

    if the_task is not None:
        the_task.transition(state)
        click.echo('Successfully transitioned {} to state {}'.format(task_id, state))
    else:
        cli_library.fail_execution(2, 'Failed to retrieve a task for key {}'.format(task_id))


@task.command()
@click.option('--username')
def score(username):
    click.echo('Scoring triage and EL tasks')

    auth = ComboAuth(username)

    try:
        triage_and_el_tasks = tasks.triage_and_el_tasks(auth)
        for current_task in triage_and_el_tasks:
            task_score = current_task.score()
            click.echo(
                "{} task's VFR updated with {} for {}".format(current_task.type_str(), task_score, current_task.id))
    except HTTPError as exception:
        cli_library.fail_execution(1, 'Task search failed with {}'.format(exception))
