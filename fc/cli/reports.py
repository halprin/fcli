import click
from ..auth.combo import ComboAuth
from ..jira import tasks
from . import cli_library
from google.oauth2 import service_account
from googleapiclient.discovery import build
import requests
from typing import Sequence
from typing import Tuple
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
    g_scopes = None
    g_service_acct_file = None
    g_sheet_create_url = None

    (g_scopes, g_service_acct_file, g_sheet_create_url) = build_google_creds(auth)

    if g_service_acct_file is None or g_sheet_create_url is None:
        cli_library.echo('Google service account credential file path and sheet create url must be defined '
                         'in order to generate a report file.')
        return

    credentials = service_account.Credentials.from_service_account_file(
        g_service_acct_file, scopes=g_scopes)

    service = build('sheets', 'v4', credentials=credentials)

    report_title = 'User Task Report {}'.format(date.today().strftime('%m-%d-%y'))

    response = requests.get(g_sheet_create_url + report_title)
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
            value_data.append(build_issue_row(user['displayName'], user_sheet_row_idx, issue))
            user_sheet_row_idx += 1

    ##################################

    cli_library.echo('retrieving unassigned, in progress tasks')

    unassigned_in_p_tasks_json = tasks.get_unassigned_in_progress_issues(auth)

    cli_library.echo('creating json for cell data update')

    add_sheet_requests.append(gen_add_sheet_req('Unassigned and In Progress'))

    user_sheet_row_idx = 1

    value_data.append({'range': '{}!A{}:H{}'.format('Unassigned and In Progress', user_sheet_row_idx,
                                                    user_sheet_row_idx),
                       'values': [['Key', 'Issue Type', 'Status', 'Summary', 'VFR', 'Due Date', 'Importance',
                                   'LOE']]})
    user_sheet_row_idx += 1

    for issue in unassigned_in_p_tasks_json['issues']:
        value_data.append(build_issue_row('Unassigned and In Progress', user_sheet_row_idx, issue))
        user_sheet_row_idx += 1

    ####################################

    cli_library.echo('retrieving unassigned, open tasks')

    unassigned_open_tasks_json = tasks.get_unassigned_open_issues(auth)

    cli_library.echo('creating json for cell data update')

    add_sheet_requests.append(gen_add_sheet_req('Unassigned and Open'))

    user_sheet_row_idx = 1

    value_data.append(
        {'range': '{}!A{}:H{}'.format('Unassigned and Open', user_sheet_row_idx, user_sheet_row_idx),
         'values': [['Key', 'Issue Type', 'Status', 'Summary', 'VFR', 'Due Date', 'Importance',
                     'LOE']]})
    user_sheet_row_idx += 1

    for issue in unassigned_open_tasks_json['issues']:
        value_data.append(build_issue_row('Unassigned and Open', user_sheet_row_idx, issue))
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
        sheet_update_requests.append(build_auto_resize_details(reply['addSheet']['properties']['sheetId'], 0, 7))

    response = service.spreadsheets().batchUpdate(
        spreadsheetId=spreadsheet_id,
        body=sheet_update).execute()

    cli_library.echo('columns of all sheets auto-resized')


@reports.command()
@click.option('--username', )
def vfrsanity(username: str):
    cli_library.echo('Generating vfr sanity check google sheet')

    auth = ComboAuth(username)

    # setup and build credentials for google api calls
    g_scopes = None
    g_service_acct_file = None
    g_sheet_create_url = None

    (g_scopes, g_service_acct_file, g_sheet_create_url) = build_google_creds(auth)

    if g_service_acct_file is None or g_sheet_create_url is None:
        cli_library.echo('Google service account credential file path and sheet create url must be defined '
                         'in order to generate a report file.')
        return

    cli_library.echo('retrieving all stories')

    # get stories ordered by duration
    jsonr = tasks.search_for_stories_ord_duration(auth)

    cli_library.echo('story retrieval complete')

    credentials = service_account.Credentials.from_service_account_file(
        g_service_acct_file, scopes=g_scopes)

    service = build('sheets', 'v4', credentials=credentials)

    report_title = 'VFR Sanity Check {}'.format(date.today().strftime('%m-%d-%y'))

    response = requests.get(g_sheet_create_url + report_title)

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
                    'title': 'Duration'
                },
                'fields': 'title'
            }
        }
    }

    response = service.spreadsheets().batchUpdate(
        spreadsheetId=spreadsheet_id,
        body=sheet_update).execute()

    cli_library.echo('default sheet title updated')

    # create arrays of data to put into the sheet
    # here's a header row
    data = [{'range': 'A1:D1',
             'values': [['Cost of Delay', 'Issue key', 'Summary', 'Duration']]}]
    row_idx = 2

    # create an array of requests that will hold "updateCells" requests
    # these are rows that will have the background color changed
    update_cells_requests = []

    update_cells = {
        'requests': update_cells_requests
    }

    # create a var to hold the "previous" duration value
    prev_duration = 0

    cli_library.echo('generating data for duration sheet cells')

    # iterate through the json results and build up all the other rows of data
    for issue in jsonr['issues']:
        # if idx > 2, then check to see if current duration val is different from "previous" val
        # if so, then add an updateCells request and increment counter, then append row of data
        # by default we always append a row of data
        if row_idx == 2:
            prev_duration = issue['fields']['customfield_18400']
        if row_idx > 2 and issue['fields']['customfield_18400'] != prev_duration:
            update_cells_requests.append(build_color_update_details(0, row_idx - 1, row_idx, 0, 5))

            prev_duration = issue['fields']['customfield_18400']
            row_idx += 1
        data.append(build_vfr_details('', row_idx, row_idx, issue))

        row_idx += 1

    update_cells_requests.append(build_auto_resize_details(0, 0, 3))

    response = service.spreadsheets().batchUpdate(
        spreadsheetId=spreadsheet_id,
        body=update_cells).execute()

    cli_library.echo('duration cell formats updated')

    body = {
        'valueInputOption': 'USER_ENTERED',
        'data': data
    }
    result = service.spreadsheets().values().batchUpdate(
        spreadsheetId=spreadsheet_id, body=body).execute()

    cli_library.echo('duration cell data updated')

    # add a second sheet to the google spreadsheet for cost of delay
    sheet_add = {
        'requests': {
            'addSheet': {
                'properties': {
                    'title': 'Cost of Delay'
                }
            }
        }
    }

    add_response = service.spreadsheets().batchUpdate(
        spreadsheetId=spreadsheet_id,
        body=sheet_add).execute()

    cli_library.echo('added cost of delay sheet')

    cod_sheet_id = add_response['spreadsheetId']
    cod_grid_id = add_response['replies'][0]['addSheet']['properties']['sheetId']

    cli_library.echo('retrieving stories for cost of delay')

    # retrieve stories ordered by cost of delay
    jsonr = tasks.search_for_stories_ord_cod(auth)

    cli_library.echo('cost of delay stories retrieved')

    # build the data for the cost of delay sheet
    data = [{'range': 'Cost of Delay!A1:D1',
             'values': [['Cost of Delay', 'Issue key', 'Summary', 'Duration']]}]
    row_idx = 2

    # create an array of requests that will hold "updateCells" requests
    # these are rows that will have the background color changed
    update_cells_requests = []

    update_cells = {
        'requests': update_cells_requests
    }

    # create a var to hold the "previous" cod value
    prev_cod = 0

    cli_library.echo('generating cell data for cost of delay sheet')

    for issue in jsonr['issues']:
        # if idx > 2, then check to see if current duration val is different from "previous" val
        # if so, then add an updateCells request and increment counter, then append row of data
        # by default we always append a row of data
        if row_idx == 2:
            prev_cod = issue['fields']['customfield_18401']
        if row_idx > 2 and issue['fields']['customfield_18401'] != prev_cod:
            update_cells_requests.append(build_color_update_details(cod_grid_id, row_idx - 1, row_idx, 0, 5))

            prev_cod = issue['fields']['customfield_18401']
            row_idx += 1
        data.append(build_vfr_details('Cost of Delay!', row_idx, row_idx, issue))

        row_idx += 1

    update_cells_requests.append(build_auto_resize_details(cod_grid_id, 0, 3))

    response = service.spreadsheets().batchUpdate(
        spreadsheetId=cod_sheet_id,
        body=update_cells).execute()

    cli_library.echo('cost of delay cell formats updated')

    body = {
        'valueInputOption': 'USER_ENTERED',
        'data': data
    }
    result = service.spreadsheets().values().batchUpdate(
        spreadsheetId=cod_sheet_id, body=body).execute()

    cli_library.echo('cost of delay cell data updated')


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


def build_google_creds(auth: ComboAuth) -> Tuple:
    scopes = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive.file']
    service_account_file = auth.google_service_acct_creds()
    sheet_create_url = auth.sheet_create_url()

    return scopes, service_account_file, sheet_create_url


def build_issue_row(display_string: str, row_index: int, issue: dict) -> dict:
    return {'range': '{}!A{}:H{}'.format(display_string,
                                         row_index, row_index),
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
                        ]]}


def build_auto_resize_details(sheet_id: dict, start_idx: int, end_idx: int) -> dict:
    return {'autoResizeDimensions': {
        'dimensions': {
            'sheetId': sheet_id,
            'dimension': 'COLUMNS',
            'startIndex': start_idx,
            'endIndex': end_idx
        }
    }}


def build_color_update_details(sheet_id: int, start_row_index: int, end_row_index: int,
                               start_column_index: int, end_column_index: int) -> dict:
    color_format_json = {
        'userEnteredFormat': {
            'backgroundColor': {
                'red': 0,
                'green': 0.4,
                'blue': 0,
                'alpha': 1.0
            }
        }
    }

    return {'updateCells': {
        'rows': [
            {
                'values': [
                    color_format_json,
                    color_format_json,
                    color_format_json,
                    color_format_json
                ]
            }
        ],
        'fields': '*',
        'range': {
            "sheetId": sheet_id,
            "startRowIndex": start_row_index,
            "endRowIndex": end_row_index,
            "startColumnIndex": start_column_index,
            "endColumnIndex": end_column_index
        }
    }}


def build_vfr_details(sheet_name: str, start_row_index: int, end_row_index: int, issue: dict) -> dict:
    return {'range': '{}A{}:D{}'.format(sheet_name, start_row_index, end_row_index),
            'values': [[issue['fields']['customfield_18401'],
                        'https://jira.cms.gov/browse/{}'.format(issue['key']),
                        issue['fields']['summary'],
                        issue['fields']['customfield_18400']
                      ]]}
