import json

from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import os.path

# Scopes
SCOPES = ['https://www.googleapis.com/auth/calendar']

def main():
    # Read the calendar settings from the JSON file
    with open('calendar_settings.json', 'r') as f:
        calendar_settings = json.load(f)
    
    if os.path.exists('token.json'):
        os.remove('token.json')

    creds = None

    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=8080)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    # Build the Google Calendar API client
    service = build('calendar', 'v3', credentials=creds)

    target_calendar_id = 'primary'

    for setting in calendar_settings:
        source_calendar_id = setting["source_calendar_id"]
        colorId = setting["colorId"]
        calendar_name = setting["calendar_name"]

        # Fetch the source events
        events_result = service.events().list(calendarId=source_calendar_id, maxResults=100).execute()
        source_events = events_result.get('items', [])

        for event in source_events:
            # Remove properties that should not be copied
            for prop in ['id', 'iCalUID', 'etag', 'htmlLink']:
                event.pop(prop, None)
            
            event["colorId"] = colorId  # Set color

            # Add the prefix to the event summary
            if "summary" in event:
                event["summary"] = f"[{calendar_name}] {event['summary']}"
            else:
                event["summary"] = f"[{calendar_name}] Untitled Event"

            print(f"Transferring event: {event['summary']}")

            # Try inserting the event into the target calendar
            try:
                service.events().insert(calendarId=target_calendar_id, body=event).execute()
            except Exception as e:
                print(f"Failed to insert event: {e}")
                

if __name__ == '__main__':
    main()