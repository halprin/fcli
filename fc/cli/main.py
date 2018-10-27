import click
from ..jira.task import Task
from requests.exceptions import HTTPError
from ..auth.combo import ComboAuth
from fc import __version__
from . import triage
from . import backlog



@click.group(invoke_without_command=True)
@click.option('--version', is_flag=True, default=False)
@click.pass_context
def cli(ctx, version):
    if version:
        click.echo(__version__)
    else:
        click.echo(ctx.get_help())


cli.add_command(triage.triage)
cli.add_command(backlog.backlog)
