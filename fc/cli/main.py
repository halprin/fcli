import click
from ..jira.task import Task
from requests.exceptions import HTTPError
from ..auth.combo import ComboAuth
from fc import __version__

@click.group(invoke_without_command=True)
@click.option('--version', is_flag=True, default=False)
@click.pass_context
def cli(ctx, version):
    if version:
        click.echo(__version__)
    else:
        click.echo(ctx.get_help())


@cli.command()
@click.argument('title')
@click.argument('description')
@click.argument('parent_story', required=False)
@click.option('--username')
@click.option('--in-progress', is_flag=True)
@click.option('--no-assign', is_flag=True)
def task(title, description, parent_story, username, in_progress, no_assign):
    click.echo('Adding task {}; {}'.format(title, description))

    auth = ComboAuth(username)

    new_task = Task(title, description, parent_story, in_progress, no_assign, auth)
    try:
        task_id, url = new_task.create()
        click.echo('{} task {} added at {}'.format(new_task.type_str(), task_id, url))
        if in_progress:
            click.echo('Triage task put into In Progress')
    except HTTPError as exception:
        click.echo('{} task creation failed with {}'.format(new_task.type_str(), exception))
