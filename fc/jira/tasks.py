import requests
from requests.auth import HTTPBasicAuth
from ..auth.auth import Auth
from . import task
from ..cli import cli_library
from typing import List
from .triage_task import TriageTask


search_url = 'https://jira.cms.gov/rest/api/2/search?maxResults=100&jql={}'


def triage_and_el_tasks(auth: Auth) -> List[TriageTask]:
    tasks = []
    raw_tasks = _search_for_triage_and_el(auth)
    cli_library.create_progressbar('Retrieving Triage and EL tasks', len(raw_tasks['issues']))
    for current_task in raw_tasks['issues']:
        cli_library.update_progressbar('Retrieving Triage and EL tasks', 1)
        tasks.append(task.Task.get_task(current_task['key'], auth))

    cli_library.finish_progressbar('Retrieving Triage and EL tasks')

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
