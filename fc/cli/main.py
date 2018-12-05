import click
from . import triage
from . import backlog
from . import el
from . import version
from . import task
from . import comment


@click.group()
def cli():
    pass


cli.add_command(triage.triage)
cli.add_command(backlog.backlog)
cli.add_command(el.el)
cli.add_command(version.version)
cli.add_command(task.task)
cli.add_command(comment.comment)
