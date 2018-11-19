import requests
from requests.auth import HTTPBasicAuth
from ..auth.auth import Auth
from . import task
from ..cli import cli_library
from typing import List
from .triage_task import TriageTask


search_url = 'https://jira.cms.gov/rest/api/2/search?jql={}'


def triage_and_el_tasks(auth: Auth) -> List[TriageTask]:
    tasks = []
    raw_tasks = _search_for_triage_and_el(auth)
    for current_task in raw_tasks['issues']:
        cli_library.echo('Retrieving info for issue: {}'.format(current_task['key']))
        tasks.append(task.Task.get_task(current_task['key'], auth))

    return tasks


def _search_for_triage_and_el(auth: Auth) -> dict:
    search_ext = 'project=qppfc+and+issueType="Triage+Task"+and+status+not+in+(resolved,closed)&fields=key,description'

    response = requests.get(search_url.format(search_ext), auth=HTTPBasicAuth(auth.username(), auth.password()))
    response.raise_for_status()

    return response.json()


def search_for_triage(auth: Auth) -> dict:
    search_ext = 'project=qppfc+and+issueType="Triage+Task"+and+(labels is empty or labels+not+in+("EL"))' +\
                 '+and+status+not+in+(resolved,closed)&fields=key,description'

    response = requests.get(search_url.format(search_ext), auth=HTTPBasicAuth(auth.username(), auth.password()))
    response.raise_for_status()

    return response.json()
