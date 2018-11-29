import click
from ..jira.comment import Comment
from requests.exceptions import HTTPError
from ..auth.combo import ComboAuth
from . import cli_library


@click.command()
@click.argument('issue_id')
@click.argument('note', metavar='"My note for the comment in quotes"')
@click.option('--username')
def comment(username: str, issue_id: str, note: str):
    click.echo("Updating issue {} with your comment '{}'".format(issue_id, note))

    auth = ComboAuth(username)

    new_comment = Comment().from_args(issue_id, note, auth)

    try:
        issue_id, url = new_comment.create()
        click.echo('Comment added to {} at {}'.format(issue_id, url))
    except HTTPError as exception:
        cli_library.fail_execution(1, 'Comment creation failed with {}'.format(exception))
