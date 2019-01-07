import click
from ..jira.issue import Issue
from ..auth.combo import ComboAuth
from . import cli_library


@click.command()
@click.option('--username')
@click.argument('issue_id')
@click.argument('note', metavar='"Your comment in quotes here."')
def comment(username: str, issue_id: str, note: str):
    click.echo('Adding comment to issue')

    auth = ComboAuth(username)

    the_issue = None

    try:
        the_issue = Issue.get_issue(issue_id, auth)
    except Exception as e:
        cli_library.fail_execution(1, 'Issue retrieval failed with {}'.format(e))

    if the_issue is not None:
        the_issue.comment(note)
        click.echo("Successfully added comment '{}' on {}".format(note, issue_id))
    else:
        cli_library.fail_execution(2, 'Failed to retrieve a task for key {}'.format(issue_id))
