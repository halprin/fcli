import click
from ..jira.backlog_task import BacklogTask
from requests.exceptions import HTTPError
from ..auth.combo import ComboAuth


@click.group()
def backlog():
    pass


@backlog.command()
@click.argument('title')
@click.argument('description')
@click.argument('parent_story')
@click.option('--username')
def create(title, description, parent_story, username):
    click.echo('Adding backlog task {}; {}'.format(title, description))

    auth = ComboAuth(username)

    new_task = BacklogTask(title, description, parent_story, auth)
    try:
        task_id, url = new_task.create()
        click.echo('Backlog task {} added at {}'.format(task_id, url))
    except HTTPError as exception:
        click.echo('Backlog task creation failed with {}'.format(exception))
