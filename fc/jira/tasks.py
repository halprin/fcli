import requests
from requests.auth import HTTPBasicAuth
from ..auth.auth import Auth
from . import task
from ..cli import cli_library


search_url = 'https://jira.cms.gov/rest/api/2/search?jql='


def triage_search(auth: Auth):
    triage_arr = []
    triage_issues = _search_for_triage(auth)
    for issue in triage_issues['issues']:
        cli_library.echo('Retrieving info for issue: {}'.format(issue['key']))
        triage_arr.append(task.Task.get_task(issue['key'], auth))

    return triage_arr


def _search_for_triage(auth: Auth) -> dict:
    search_ext = 'project=qppfc+and+issueType="Triage+Task"+and+(labels is empty or labels+not+in+("EL"))' +\
                 '+and+status+not+in+(resolved,closed)&fields=key,description'

    response = requests.get(search_url + search_ext, auth=HTTPBasicAuth(auth.username(), auth.password()))
    response.raise_for_status()

    return response.json()
