import click
from ..auth.combo import ComboAuth
from ..jira import tasks
from . import cli_library
from google.oauth2 import service_account
from googleapiclient.discovery import build
import requests
from datetime import date


@click.group()
def vfrsanity():
    pass


@vfrsanity.command()
@click.option('--username', )
def check(username: str):
    cli_library.echo('Generating vfr sanity check google sheet')

    auth = ComboAuth(username)

    SERVICE_ACCOUNT_FILE = auth.google_service_acct_creds()
    SHEET_CREATE_URL = auth.sheet_create_url()

    if SERVICE_ACCOUNT_FILE is None or SHEET_CREATE_URL is None:
        cli_library.echo('Google service account credential file path and sheet create url must be defined '
                         'in order to generate a report file.')

    cli_library.echo('retrieving all stories')

    # get stories ordered by duration
    jsonr = tasks.search_for_stories_ord_duration(auth)

    cli_library.echo('story retrieval complete')

    # setup and build credentials for google api calls
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive.file']

    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)

    service = build('sheets', 'v4', credentials=credentials)

    report_title = 'VFR Sanity Check ' + date.today().strftime('%m-%d-%y')

    response = requests.get(SHEET_CREATE_URL + report_title)

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
    idx = 2

    # create an array of requests that will hold "updateCells" requests
    # these are rows that will have the background color changed
    update_cells_requests = []

    update_cells = {
        'requests': update_cells_requests
    }

    # create a var to hold the "previous" duration value
    prev_duration = 0

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

    cli_library.echo('generating data for duration sheet cells')

    # iterate through the json results and build up all the other rows of data
    for issue in jsonr['issues']:
        # if idx > 2, then check to see if current duration val is different from "previous" val
        # if so, then add an updateCells request and increment counter, then append row of data
        # by default we always append a row of data
        if idx == 2:
            prev_duration = issue['fields']['customfield_18400']
        if idx > 2 and issue['fields']['customfield_18400'] != prev_duration:
            update_cells_requests.append({'updateCells': {
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
                                                      "sheetId": 0,
                                                      "startRowIndex": idx - 1,
                                                      "endRowIndex": idx,
                                                      "startColumnIndex": 0,
                                                      "endColumnIndex": 5
                                              }
                                            }})
            prev_duration = issue['fields']['customfield_18400']
            idx += 1
        data.append({'range': 'A{}:D{}'.format(idx, idx),
                     'values': [[issue['fields']['customfield_18401'],
                                 'https://jira.cms.gov/browse/{}'.format(issue['key']),
                                 issue['fields']['summary'],
                                 issue['fields']['customfield_18400']
                                 ]]})
        idx += 1

    update_cells_requests.append({'autoResizeDimensions': {
                                        'dimensions': {
                                            'sheetId': 0,  # the default sheet id is always 0
                                            'dimension': 'COLUMNS',
                                            'startIndex': 0,
                                            'endIndex': 3
                                        }
                                  }})

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
    idx = 2

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
        if idx == 2:
            prev_cod = issue['fields']['customfield_18401']
        if idx > 2 and issue['fields']['customfield_18401'] != prev_cod:
            update_cells_requests.append({'updateCells': {
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
                    "sheetId": cod_grid_id,
                    "startRowIndex": idx - 1,
                    "endRowIndex": idx,
                    "startColumnIndex": 0,
                    "endColumnIndex": 5
                }
            }})
            prev_cod = issue['fields']['customfield_18401']
            idx += 1
        data.append({'range': 'Cost of Delay!A{0}:D{0}'.format(idx),
                     'values': [[issue['fields']['customfield_18401'],
                                 'https://jira.cms.gov/browse/{0}'.format(issue['key']),
                                 issue['fields']['summary'],
                                 issue['fields']['customfield_18400']
                                 ]]})
        idx += 1

    update_cells_requests.append({'autoResizeDimensions': {
                                    'dimensions': {
                                        'sheetId': cod_grid_id,
                                        'dimension': 'COLUMNS',
                                        'startIndex': 0,
                                        'endIndex': 3
                                    }
                                }})

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
