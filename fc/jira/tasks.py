import requests
from . import issue
from requests.auth import HTTPBasicAuth
from requests.exceptions import HTTPError
from ..auth.auth import Auth
from ..cli import cli_library
from concurrent.futures import ThreadPoolExecutor
import asyncio


search_url = 'https://jira.cms.gov/rest/api/2/search?maxResults=100&jql={}'


def score_triage_and_el_tasks(auth: Auth):
    try:
        raw_tasks = _search_for_triage_and_el(auth)
    except HTTPError as exception:
        cli_library.fail_execution(1, 'Task search failed with {}'.format(exception))

    awaitables = []
    for current_task in raw_tasks['issues']:
        scoring_task = asyncio.ensure_future(_score_triage_and_el_task(current_task['key'], auth))
        awaitables.append(scoring_task)

    loop = asyncio.get_event_loop()
    scoring_results = loop.run_until_complete(asyncio.gather(*awaitables, return_exceptions=True))
    loop.close()

    scoring_results_exception = [scoring_result for scoring_result in scoring_results if
                                 scoring_result is not None and isinstance(scoring_result, Exception)]
    for scoring_exception in scoring_results_exception:
        cli_library.echo('Task scoring failed for one of the tasks with {}'.format(scoring_exception))
    if len(scoring_results_exception) > 0:
        cli_library.fail_execution(1, 'Task scoring failed')


async def _score_triage_and_el_task(task_key: str, auth: Auth):
    loop = asyncio.get_event_loop()
    with ThreadPoolExecutor() as executor:
        cli_library.echo('Retrieving {}'.format(task_key))
        scorable_task = await loop.run_in_executor(executor, issue.Issue.get_issue, task_key, auth)
        task_score = await loop.run_in_executor(executor, scorable_task.score)
        cli_library.echo(
            "{} task's VFR updated with {} for {}".format(scorable_task.type_str(), task_score, scorable_task.id))


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
