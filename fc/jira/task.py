import requests
from requests.auth import HTTPBasicAuth


class Task:
    api_url = 'https://jira.cms.gov/rest/api/2/issue/'
    base_url = 'https://jira.cms.gov/browse/{}'

    def __init__(self, title: str, description: str):
        self.title = title
        self.description = description
        self.id = None
        self.url = None

    def create(self):
        json = {
            'fields': {
                'project': {
                    'key': 'QPPFC'
                },
                'summary': self.title,
                'description': self.description,
                'issuetype': {
                    'name': 'Triage Task'
                },
                'components': [{
                    'name': 'Foundational'
                }]
            }
        }

        response = requests.post(self.api_url, json=json, auth=HTTPBasicAuth('', ''))
        response.raise_for_status()

        response_json = response.json()
        # {"id":"491588","key":"QPPFC-301","self":"https://jira.cms.gov/rest/api/2/issue/491588"}
        self.id = response_json['key']
        self.url = self.base_url.format(self.id)

        return self.id, self.url
