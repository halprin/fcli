import datetime
import re
import requests
from requests.auth import HTTPBasicAuth
from .task import Task

search_url = 'https://jira.cms.gov/rest/api/2/search?jql='

importance_dict = {
    'High': 10,
    'high': 10,
    'Medium': 5,
    'medium': 5,
    'Low': 1,
    'low': 1
}

loe_dict = {
    'High': 1,
    'high': 1,
    'Medium': 5,
    'medium': 5,
    'Low': 10,
    'low': 10
}

date_dict = {
    (0, 7): 20,
    (8, 14): 15,
    (15, 28): 10,
    (29, 42): 5
}


def triage_search(auth) -> dict:
    return _search_for_triage(auth)


def score(task, auth):
    (imp_part, loe_part, date_part) = _find_triage_score_parts(task)
    score = _calc_triage_score(imp_part, loe_part, date_part)
    _update_triage_vfr(task['key'], score, auth)


def _search_for_triage(auth) -> dict:
    search_ext = 'project=qppfc+and+issueType="Triage+Task"+and+status+not+in+(resolved,closed)&fields=key,description'

    response = requests.get(search_url + search_ext,
                            auth=HTTPBasicAuth(auth.username(), auth.password()))
    response.raise_for_status()

    return response


def _find_triage_score_parts(task) -> (str, str, str):
    regex = 'Importance: (.*)\\r\\n\\r\\nLOE: (.*)\\r\\n\\r\\nDate [N|n]eeded: (.*)\\r\\n\\r\\n'

    m = re.search(regex, task['fields']['description'], re.MULTILINE)
    if m is None:
        return (None, None, None)
    else:
        return m.groups()


def _calc_triage_score(imp_part, loe_part, date_part) -> int:

    dt_score = 0

    imp_score = importance_dict.get(imp_part, 0)

    loe_score = loe_dict.get(loe_part, 0)

    try:
        dt_obj = datetime.datetime.strptime(date_part, '%m/%d/%Y')

        today = datetime.datetime.today()

        day_diff = (dt_obj - today).days

        dt_score = _get_date_score(day_diff)

    except (ValueError, TypeError):
        dt_score = 0

    return (imp_score + loe_score + dt_score)


def _update_triage_vfr(issue, score, auth):
    json = {
        'fields': {
            'customfield_18402': score
        }
    }

    # custom field for VFR = customfield_18402

    response = requests.put(Task.api_url + issue, json=json,
                            auth=HTTPBasicAuth(auth.username(), auth.password()))
    response.raise_for_status()


def _get_date_score(num_days) -> int:

    for key in date_dict:
        if key[0] <= num_days <= key[1]:
            return date_dict[key]

    return 0
