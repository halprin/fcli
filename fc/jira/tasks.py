import requests
from . import issue
from requests.auth import HTTPBasicAuth
from requests.exceptions import HTTPError
from ..auth.auth import Auth
from ..cli import cli_library
from concurrent.futures import ThreadPoolExecutor
import asyncio


search_url = 'https://jira.cms.gov/rest/api/2/search?maxResults=400&jql={}'


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


def search_for_stories_ord_duration(auth: Auth) -> dict:
    search_ext = 'project=qppfc+and+type="Story"+and+status+in+(refined,blocked,ready,"in+progress")+order+by+' +\
                 'duration+desc,+key+asc&fields=key,summary,customfield_18402,customfield_18400,customfield_18401'

    response = requests.get(search_url.format(search_ext), auth=HTTPBasicAuth(auth.username(), auth.password()))
    response.raise_for_status()

    return response.json()


def search_for_stories_ord_cod(auth: Auth) -> dict:
    search_ext = 'project=qppfc+and+type="Story"+and+status+in+(refined,blocked,ready,"in+progress")+order+by+' +\
                 '"cost of delay"+desc,+key+asc&fields=key,summary,customfield_18402,customfield_18400,' +\
                 'customfield_18401'

    response = requests.get(search_url.format(search_ext), auth=HTTPBasicAuth(auth.username(), auth.password()))
    response.raise_for_status()

    return response.json()


def get_developer_users(auth: Auth) -> dict:
    response = requests.get('https://jira.cms.gov/rest/api/2/project/20101/role/10001',
                            auth=HTTPBasicAuth(auth.username(), auth.password()))
    response.raise_for_status()

    return response.json()


def get_user_issues(user: str, auth: Auth) -> dict:
    search_ext = 'project=qppfc+and+assignee={}+and+status+in+(refined,blocked,ready,"in+progress",triage,open)+'.format(user) +\
                 'order+by+duration+asc&fields=key,summary,issuetype,status,customfield_18402,customfield_18400,' +\
                 'customfield_18401,customfield_19905,customfield_19904,customfield_13405,labels'

    # cli_library.echo('search url: {}'.format(search_url.format(search_ext)))

    response = requests.get(search_url.format(search_ext), auth=HTTPBasicAuth(auth.username(), auth.password()))
    response.raise_for_status()

    return response.json()


def get_unassigned_in_progress_issues(auth: Auth) -> dict:
    search_ext = 'project=qppfc+and+assignee+is+empty+and' +\
                 '+status+in+(refined,blocked,ready,%22in+progress%22)+and+issuetype+not+in+(Story,Epic)+order' +\
                 '+by+duration+asc&fields=key,summary,issuetype,status,customfield_18402,customfield_18400,' +\
                 'customfield_18401,customfield_19905,customfield_19904,customfield_13405,labels'

    response = requests.get(search_url.format(search_ext), auth=HTTPBasicAuth(auth.username(), auth.password()))
    response.raise_for_status()

    return response.json()


def get_unassigned_open_issues(auth: Auth) -> dict:
    search_ext = 'project=qppfc+and+assignee+is+empty+and' +\
                 '+status+not+in+(refined,blocked,ready,"in+progress",Resolved,Closed)+and+issuetype+not+in+' +\
                 '(Story,Epic)+order' +\
                 '+by+duration+asc&fields=key,summary,issuetype,status,customfield_18402,customfield_18400,' +\
                 'customfield_18401,customfield_19905,customfield_19904,customfield_13405,labels'

    response = requests.get(search_url.format(search_ext), auth=HTTPBasicAuth(auth.username(), auth.password()))
    response.raise_for_status()

    return response.json()
