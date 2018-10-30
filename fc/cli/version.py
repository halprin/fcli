import click
from fc import __version__

@click.command()	
def version():	
    print(__version__)