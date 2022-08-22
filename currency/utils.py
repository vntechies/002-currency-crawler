import os
import google.auth
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = './credentials.json'
SPREADSHEET_ID = os.environ.get('SPREADSHEET_ID')
RANGE_NAME = os.environ.get('RANGE_NAME')
VALUE_INPUT_OPTION = os.environ.get('VALUE_INPUT_OPTION')

def append_to_db(values):
    creds, _ = google.auth.default()
    try:
        service = build('sheets', 'v4', credentials=creds)
        # ["2022/03/17", "MBB", "23020", "25876", "198.31", "16962", "2996", "17169"]
        body = {
            'values': [values]
        }
        result = service.spreadsheets().values().append(
            spreadsheetId=SPREADSHEET_ID, range=RANGE_NAME,
            valueInputOption=VALUE_INPUT_OPTION, body=body).execute()
        print(f"{(result.get('updates').get('updatedCells'))} cells appended.")
        return result

    except HttpError as error:
        print(f"An error occurred: {error}")
        return error

# date bank USD	EUR	JPY	AUD	HKD	SGD
def format_record(record):
    arr = []
    arr.append(record['date'])
    arr.append(record['bank'])
    arr.append(record['USD'])
    arr.append(record['EUR'])
    arr.append(record['JPY'])
    arr.append(record['AUD'])
    arr.append(record['HKD'])
    arr.append(record['SGD'])
    return arr
    