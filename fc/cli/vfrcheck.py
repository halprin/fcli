import click
from ..jira.fcissue import FcIssue
from ..auth.combo import ComboAuth
from ..jira import tasks
from . import cli_library
from ..exceptions.task_exception import TaskException


@click.group()
def vfrsanity():
    pass


@vfrsanity.command()
@click.option('--username')
def check(username: str):
    cli_library.echo('Generating duration CSV')

    auth = ComboAuth(username)

    jsonr = tasks.search_for_stories(auth)

    # iterate through issues in jsonr
    #



    # the_task = None
    #
    # try:
    #     # use a factory method to GET the issue by key
    #     the_task = FcIssue.get_issue(task_id, auth)
    # except TaskException as exception:
    #     cli_library.fail_execution(1, 'Task search failed with {}'.format(exception))
    #
    # if the_task is not None:
    #     the_task.transition(state)
    #     cli_library.echo('Successfully transitioned {} to state {}'.format(task_id, state))
    # else:
    #     cli_library.fail_execution(2, 'Failed to retrieve a task for key {}'.format(task_id))
