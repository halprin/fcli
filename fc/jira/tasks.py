import requests
from requests import HTTPError
from requests.auth import HTTPBasicAuth

from fc.exceptions.task_exception import TaskException
from ..auth.auth import Auth


search_url = 'https://jira.cms.gov/rest/api/2/search?jql='
api_url = 'https://jira.cms.gov/rest/api/2/issue/'


def triage_search(auth: Auth):
    triage_arr = []
    triage_issues = _search_for_triage(auth)
    for issue in triage_issues['issues']:
        print('Retrieving info for issue: {}'.format(issue['key']))
        triage_arr.append(get_task(api_url, issue['key'], auth))

    return triage_arr


def _search_for_triage(auth: Auth) -> dict:
    search_ext = 'project=qppfc+and+issueType="Triage+Task"+and+(labels is empty or labels+not+in+("EL"))' +\
                 '+and+status+not+in+(resolved,closed)&fields=key,description'

    response = requests.get(search_url + search_ext, auth=HTTPBasicAuth(auth.username(), auth.password()))
    response.raise_for_status()

    return response.json()


def get_issue(api_url: str, issue_id: str, auth: Auth) -> dict:
    response = requests.get(api_url + issue_id,
                            auth=HTTPBasicAuth(auth.username(), auth.password()))
    response.raise_for_status()

    return response.json()


def get_task(api_url: str, issue_id: str, auth: Auth):
    from .backlog_task import BacklogTask
    from .triage_task import TriageTask

    issue_json = {}
    new_task = None

    try:
        issue_json = get_issue(api_url, issue_id, auth)
    except HTTPError as exception:
        raise TaskException('Invalid issue key {}'.format(issue_id)) from exception

    type = issue_json['fields']['issuetype']['name']
    if type != 'Task' and type != 'Triage Task':
        raise TaskException('Invalid issue type {}'.format(type))
    elif type == 'Task':
        new_task = BacklogTask.from_json(issue_json, auth)
    else:
        new_task = TriageTask.from_json(issue_json, auth)

    return new_task
