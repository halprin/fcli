import click
from typing import Sequence

_progress_bars = {}


def echo(text):
    click.echo(text)


def create_progressbar(label, length):
    progress_bar = click.progressbar(length=length, label=label)
    _progress_bars[label] = progress_bar


def update_progressbar(label, amount):
    _progress_bars[label].update(amount)


def finish_progressbar(label):
    _progress_bars[label].finish()
    click.echo('')


def fail_execution(return_code: int, error_string: str):
    exit_exception = click.ClickException(error_string)
    exit_exception.exit_code = return_code
    raise exit_exception


# This allows us to call up a click prompt from different parts of the flow
def prompt(the_prompt: str, choices: Sequence[str]) -> str:

    if choices is None:
        return click.prompt(the_prompt)
    else:
        return click.prompt(the_prompt, type=click.Choice(choices))
