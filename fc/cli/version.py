import click
from fc import __version__


@click.command()
def version():
    click.echo(__version__)
