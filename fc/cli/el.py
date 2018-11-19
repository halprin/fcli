import click
from ..jira.el_task import ElTask
from requests.exceptions import HTTPError
from ..auth.combo import ComboAuth
import click_datetime


@click.group()
def el():
    pass


@el.command()
@click.argument('title')
@click.argument('description')
@click.option('--username')
@click.option('--in-progress', is_flag=True)
@click.option('--no-assign', is_flag=True)
@click.option('--importance', prompt=True, type=click.Choice(['Low', 'Medium', 'High'], case_sensitive=False))
@click.option('--effort', prompt='Level of Effort', type=click.Choice(['Low', 'Medium', 'High'], case_sensitive=False))
@click.option('--due', prompt='Due date (mm/dd/yyyy)', type=click_datetime.Datetime(format='%m/%d/%Y'))
def create(title, description, username, in_progress, no_assign, importance, effort, due):
    click.echo('Adding EL task {}; {}'.format(title, description))

    auth = ComboAuth(username)

    new_task = ElTask.from_args(title, description, in_progress, no_assign, importance, effort, due, auth)
    try:
        task_id, url = new_task.create()
        click.echo('EL task {} added at {}'.format(task_id, url))
        if in_progress:
            click.echo('EL task put into In Progress')
    except HTTPError as exception:
        click.echo('EL task creation failed with {}'.format(exception))