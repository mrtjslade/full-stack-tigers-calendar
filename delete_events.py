from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import os.path

# If modifying these SCOPES, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/calendar']

def main():
    """Shows basic usage of the Google Calendar API."""
    if os.path.exists('token.json'):
            os.remove('token.json')

    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, prompt the user to log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=8080)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    
    # Initialize the Calendar API
    service = build('calendar', 'v3', credentials=creds)
    
    # Ask the user for the calendar ID
    # calendar_id = input("Enter the Calendar ID: ")
    calendar_id = 'fullstacktigers@gmail.com'

    # Fetch the list of events from the specified calendar
    print('Fetching the upcoming events')
    events_result = service.events().list(calendarId=calendar_id, maxResults=2500).execute()
    events = events_result.get('items', [])

    # Check if there are any events to delete
    if not events:
        print('No upcoming events found.')
        return

    # Loop through the list of events and delete each one
    for event in events:
        event_id = event['id']
        print(f"Deleting event {event['summary']}...")
        service.events().delete(calendarId=calendar_id, eventId=event_id).execute()

    print('All events deleted.')

if __name__ == '__main__':
    main()