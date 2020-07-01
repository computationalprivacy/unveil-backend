"""Opted out MAC addresses retrieval."""
from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client.service_account import ServiceAccountCredentials
from django.conf import settings
from db_manager.models import get_optout_collection
import datetime


def get_opted_out_mac_from_db():
    """Return list of mac opted out, from db."""
    optout_collection = get_optout_collection()
    mac_addresses = [obj['mac'].lower() for obj in optout_collection.find(
        {}, {'mac': 1, '_id': 0})]
    return mac_addresses


def ingest_opted_out_mac(mac_values):
    """Ingest opted out MAC addresses into the mongo db."""
    optout_collection = get_optout_collection()
    count = 0
    for mac_val in mac_values:
        mac = mac_val[0].lower()
        optout_collection.replace_one(
            {'mac': mac},
            {'mac': mac, 'created_at': datetime.datetime.now()},
            upsert=True)
        count += 1
    print("Total opted out {} mac addresses.".format(count))


def get_opted_out_mac_from_form():
    """Show basic usage of the Sheets API.

    Prints values from a sample spreadsheet.
    """
    # use creds to create a client to interact with the Google Drive API
    scope = ['https://spreadsheets.google.com/feeds']
    creds = ServiceAccountCredentials.from_json_keyfile_name(
        'google_api_creds.json', scope)
    # store = file.Storage('token.json')
    # creds = store.get()
    # if not creds or creds.invalid:
    #     flow = client.flow_from_clientsecrets('credentials.json', SCOPES)
    #     creds = tools.run_flow(flow, store)
    service = build('sheets', 'v4', http=creds.authorize(Http()))

    # Call the Sheets API
    sheet = service.spreadsheets()
    result = sheet.values().get(
        spreadsheetId=settings.OPTOUT_SPREADSHEET_ID,
        range=settings.OPTOUT_RANGE_NAME).execute()
    values = result.get('values', [])
    print(values)
    return values


def get_opted_out_mac():
    """Return opted out mac addresses.

    If the last ingest had happened less than 10 minutes before the
    current time then mac addresses in mongo are not updated.

    """
    ingest_opted_out_mac(get_opted_out_mac_from_form())
    return get_opted_out_mac_from_db()
