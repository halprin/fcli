import click
from fc import __version__
from . import triage
from . import backlog
from . import version


@click.group()
def cli():
    pass


cli.add_command(triage.triage)
cli.add_command(backlog.backlog)
cli.add_command(version.version)
