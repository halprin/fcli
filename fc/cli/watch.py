import click
from ..jira.issue import Issue
from ..auth.combo import ComboAuth
from . import cli_library


@click.command()
@click.option('--username')
@click.argument('issue_ids', nargs=-1, metavar='ISSUE-1 ISSUE-2 ISSUE-3 etc.')
def watch(username: str, issue_ids: tuple):
    auth = ComboAuth(username)

    uname = auth.username()

    for i in issue_ids:
        click.echo("Adding '{}' to the watchlist for {}".format(uname, i))

        the_issue = None

        try:
            the_issue = Issue.get_issue(i, auth)
        except Exception as e:
            cli_library.fail_execution(1, 'Issue retrieval failed with {}'.format(e))

        if the_issue is not None:
            the_issue.watch(uname)
            click.echo("Successfully added '{}' to {}".format(auth.username(), i))
        else:
            cli_library.fail_execution(2, 'Failed to modify watchlist for {}'.format(i))
