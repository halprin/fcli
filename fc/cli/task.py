import click
from ..jira.fcissue import FcIssue
from ..jira.issue import Issue
from ..auth.combo import ComboAuth
from ..jira import tasks
from . import cli_library
from ..exceptions.task_exception import TaskException
from requests import HTTPError


@click.group()
def task():
    pass


@task.command()
@click.option('--username')
@click.argument('task_id')
@click.argument('state')
@click.option('--resolution')
@click.option('--comment')
def move(username: str, task_id: str, state: str, resolution: str, comment: str):

    if state in ['Resolved', 'Closed']:
        if resolution is None:
            resolution = cli_library.prompt('Please enter a resolution',
                                            ['Fixed', 'Duplicate', 'Done', 'Won\'t Do'])

    auth = ComboAuth(username)

    the_task = None

    try:
        # use a factory method to GET the issue by key
        the_task = FcIssue.get_issue(task_id, auth)
    except TaskException as exception:
        cli_library.fail_execution(1, 'Task search failed with {}'.format(exception))

    if the_task is not None:
        the_task.transition(state, resolution, comment)
        cli_library.echo('Successfully transitioned {} to state {}'.format(task_id, state))
    else:
        cli_library.fail_execution(2, 'Failed to retrieve a task for key {}'.format(task_id))


@task.command()
@click.option('--username')
def score(username):
    cli_library.echo('Scoring triage and EL tasks')

    auth = ComboAuth(username)

    tasks.score_triage_and_el_tasks(auth)


@task.command()
@click.option('--username')
@click.argument('task_ids', nargs=-1, metavar='ISSUE-1 ISSUE-2 ISSUE-3 etc.')
def watch(username: str, task_ids: tuple):
    auth = ComboAuth(username)

    for task_id in task_ids:
        cli_library.echo("Adding '{}' to the watchlist for {}".format(auth.username(), task_id))

        try:
            the_task = Issue.get_issue(task_id, auth)
        except HTTPError as e:
            cli_library.fail_execution(1, 'Issue retrieval failed with {}'.format(e))

        try:
            the_task.watch(auth.username())
            cli_library.echo("Successfully added '{}' to {}".format(auth.username(), task_id))
        except HTTPError as e:
            cli_library.fail_execution(2, 'Failed to modify watchlist for {}'.format(task_id))
