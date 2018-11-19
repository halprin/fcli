import click


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


def fail_execution(return_code: int, error_string: str):
    exit_exception = click.ClickException(error_string)
    exit_exception.exit_code = return_code
    raise exit_exception
