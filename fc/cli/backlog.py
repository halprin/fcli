import click

from fc.jira.backlog_story import BacklogStory
from ..jira.issue import Issue
from ..jira.backlog_task import BacklogTask
from requests.exceptions import HTTPError
from ..auth.combo import ComboAuth
from . import cli_library


@click.group()
def backlog():
    pass


@backlog.group()
def create():
    pass


@create.command()
@click.argument('title')
@click.argument('description')
@click.argument('parent_story')
@click.option('--username')
def task(title: str, description: str, parent_story: str, username: str):
    cli_library.echo('Adding backlog task {}; {}'.format(title, description))

    auth = ComboAuth(username)

    new_task = BacklogTask.from_args(title, description, parent_story, auth)

    try:
        task_id, url = new_task.create()
        cli_library.echo('Backlog task {} added at {}'.format(task_id, url))
    except HTTPError as exception:
        cli_library.fail_execution(1, 'Backlog task creation failed with {}'.format(exception))


@create.command()
@click.argument('title')
@click.option('--description', prompt='Description')
@click.option('--ac', prompt='Acceptance Criteria')
@click.option('--username')
def story(title: str, description: str, ac: str, username: str):
    cli_library.echo('Adding backlog story {}'.format(title))

    auth = ComboAuth(username)

    new_story = BacklogStory.from_args(title, description, ac, auth)

    try:
        task_id, url = new_story.create()
        cli_library.echo('Backlog story {} added at {}'.format(task_id, url))
    except HTTPError as exception:
        cli_library.fail_execution(1, 'Backlog story creation failed with {}'.format(exception))


@backlog.command()
@click.argument('issue_id')
@click.argument('duration', type=int)
@click.argument('cost_of_delay', type=int)
@click.option('--username')
def score(issue_id: str, duration: int, cost_of_delay: int, username: str):
    cli_library.echo('Adding VFR to issue')

    auth = ComboAuth(username)

    the_issue = None

    try:
        the_issue = Issue.get_issue(issue_id, auth)
    except Exception as e:
        cli_library.fail_execution(1, 'Issue retrieval failed with {}'.format(e))

    if the_issue is not None:
        if the_issue.project == 'QPPFC' and the_issue.type_str() == 'Story':
            the_issue.set_duration(duration)
            the_issue.set_cost_of_delay(cost_of_delay)
            vfr_value = the_issue.score()
            cli_library.echo('Successfully updated {} with a VFR of {}'.format(issue_id, vfr_value))
        else:
            err_string = 'Failed to update VFR, issue {} is not a backlog story [{}] or is not the correct project [{}]'
            cli_library.fail_execution(3, err_string.format(issue_id, the_issue.type_str(), the_issue.project))
    else:
        cli_library.fail_execution(2, 'Failed to retrieve an issue for key {}'.format(issue_id))
