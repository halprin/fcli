import click
from ..jira.issue import Issue
from ..auth.combo import ComboAuth
from . import cli_library
from requests import HTTPError


@click.command()
@click.option('--username')
@click.argument('issue_ids', nargs=-1, metavar='ISSUE-1 ISSUE-2 ISSUE-3 etc.')
def watch(username: str, issue_ids: tuple):
    auth = ComboAuth(username)

    for issue_id in issue_ids:
        cli_library.echo("Adding '{}' to the watchlist for {}".format(auth.username(), issue_id))

        the_issue = None

        try:
            the_issue = Issue.get_issue(issue_id, auth)
        except Exception as e:
            cli_library.fail_execution(1, 'Issue retrieval failed with {}'.format(e))

        try:
            the_issue.watch(auth.username())
            cli_library.echo("Successfully added '{}' to {}".format(auth.username(), issue_id))
        except HTTPError as e:
            cli_library.fail_execution(2, 'Failed to modify watchlist for {}'.format(issue_id))
