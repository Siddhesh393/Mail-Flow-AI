import gspread
from utils.google_auth import get_credentials

SPREADSHEET_NAME = "MailFlow_AI_Tracker"


def get_sheets_client():
    creds = get_credentials()
    return gspread.authorize(creds)


def get_sheet(sheet_name: str = SPREADSHEET_NAME):
    client = get_sheets_client()
    return client.open(sheet_name)
