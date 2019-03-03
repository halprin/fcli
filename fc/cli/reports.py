import click
from ..auth.combo import ComboAuth
from ..jira import tasks
from . import cli_library
from google.oauth2 import service_account
from googleapiclient.discovery import build
import requests
from typing import Sequence
from datetime import date


@click.group()
def reports():
    pass


@reports.command()
@click.option('--username', )
def usertasks(username: str):
    cli_library.echo('Generating user tasks to google sheet')

    auth = ComboAuth(username)

    # setup and build credentials for google api calls
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive.file']
    SERVICE_ACCOUNT_FILE = '/Users/sfradkin/.fcli/quickstart-1549666983080-fdb14a0d013a.json'

    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)

    service = build('sheets', 'v4', credentials=credentials)

    base_create_sheet_url = 'https://script.google.com/macros/s/AKfycbw_mh_P6b50yHADcYku4LCmkLhoxjtWIsY2NlxoDHTG' \
                            'fiz4s4-l/exec?shareWith=fcli-user@quickstart-1549666983080.iam.gserviceaccount.com&' \
                            'title='

    report_title = 'User Task Report ' + date.today().strftime('%d-%m-%y')

    response = requests.get(base_create_sheet_url + report_title)
    response.raise_for_status()

    response_json = response.json()

    spreadsheet_id = None
    folder_id = None

    if response_json['success']:
        spreadsheet_id = response_json['newSheetId']
        folder_id = response_json['destFolderId']
        cli_library.echo('successful spreadsheet creation, https://docs.google.com/spreadsheets/d/{}/edit#gid=0, '
                         .format(spreadsheet_id) +
                         'folder: {}'.format(folder_id))

    # update the individual sheet name in the spreadsheet we just created
    sheet_update = {
        'requests': {
            'updateSheetProperties': {
                'properties': {
                    'title': 'Names'
                },
                'fields': 'title'
            }
        }
    }

    response = service.spreadsheets().batchUpdate(
        spreadsheetId=spreadsheet_id,
        body=sheet_update).execute()

    cli_library.echo('first sheet title updated')

    # add data header row for names sheet
    # get users
    # iterate through users
    #   add data row to name sheet with name
    #   create an add sheet request for the user
    #   create a data header row for user sheet
    #   get tasks for user
    #     add data row to user sheet for each task: key (link), issue type, summary, status, vfr, due date, importance
    #     , loe
    # execute batch update for adding all sheets
    # execute batch update for adding all data

    value_data = []
    add_sheet_requests = []
    add_sheet = {
        'requests': add_sheet_requests
    }
    data_body = {
        'valueInputOption': 'USER_ENTERED',
        'data': value_data
    }

    name_sheet_row_idx = 1

    value_data.append({'range': 'A{}:B{}'.format(name_sheet_row_idx, name_sheet_row_idx),
                       'values': [['Name', 'EUA']]})
    name_sheet_row_idx += 1

    dev_user_json = tasks.get_developer_users(auth)

    user_sheet_row_idx = 1
    user_tasks_json = None

    for user in dev_user_json['actors']:
        value_data.append({'range': 'A{}:B{}'.format(name_sheet_row_idx, name_sheet_row_idx),
                           'values': [[user['displayName'], user['name']]]})
        name_sheet_row_idx += 1

        add_sheet_requests.append(gen_add_sheet_req(user['displayName']))

        user_sheet_row_idx = 1

        value_data.append({'range': '{}!A{}:H{}'.format(user['displayName'], user_sheet_row_idx, user_sheet_row_idx),
                           'values': [['Key', 'Issue Type', 'Status', 'Summary', 'VFR', 'Due Date', 'Importance',
                                      'LOE']]})
        user_sheet_row_idx += 1

        user_tasks_json = tasks.get_user_issues(user['name'], auth)

        cli_library.echo('creating json for cell data update')

        for issue in user_tasks_json['issues']:
            value_data.append({'range': '{}!A{}:H{}'.format(user['displayName'],
                                                            user_sheet_row_idx, user_sheet_row_idx),
                               'values': [['https://jira.cms.gov/browse/{}'.format(issue['key']),
                                          'EL Task' if is_el(issue['fields']['labels'])
                                           else issue['fields']['issuetype']['name'],
                                           issue['fields']['status']['name'],
                                           issue['fields']['summary'],
                                           issue['fields']['customfield_18402'],
                                           issue['fields']['customfield_19905'],
                                           issue['fields']['customfield_19904']['value']
                                           if issue['fields'].get('customfield_19904') is not None else None,
                                           issue['fields']['customfield_13405']['value']
                                           if issue['fields'].get('customfield_13405') is not None else None
                                           ]]})
            user_sheet_row_idx += 1

        # execute batch update for adding all sheets
        # execute batch update for adding all data

    add_response = service.spreadsheets().batchUpdate(
        spreadsheetId=spreadsheet_id,
        body=add_sheet).execute()

    cli_library.echo('new sheets for each developer added')

    data_response = service.spreadsheets().values().batchUpdate(
        spreadsheetId=spreadsheet_id,
        body=data_body).execute()

    cli_library.echo('data added to sheets')

    sheet_update_requests = []

    sheet_update = {
        'requests': sheet_update_requests
    }

    for reply in add_response['replies']:
        sheet_update_requests.append({'autoResizeDimensions': {
                                        'dimensions': {
                                          'sheetId': reply['addSheet']['properties']['sheetId'],
                                          'dimension': 'COLUMNS',
                                          'startIndex': 0,
                                          'endIndex': 7
                                    }
                                }})

    response = service.spreadsheets().batchUpdate(
        spreadsheetId=spreadsheet_id,
        body=sheet_update).execute()

    cli_library.echo('columns of all sheets auto-resized')


def gen_add_sheet_req(sheet_name: str) -> dict:

    req = {
        'addSheet': {
            'properties': {
                'title': sheet_name
            }
        }
    }

    return req


def is_el(labels: Sequence[str]) -> bool:
    for label in labels:
        if label == 'EL':
            return True
        else:
            return False
