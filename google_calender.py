import os.path
import datetime as dt

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SCOPES = ["https://www.googleapis.com/auth/calender"]

def main():
    creds = None

    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json")

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow =  InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)
        with open("token.json", "w") as token :
            token.write(creds.to_json())

    try:
        service = build("calendar", "v3", Credentials = creds)

        now = dt.datetime.now().isoformat() + "2"
        # pass
        event_result = service.events.list(calendarId ="primary", timeMin=now, maxResults = 10, singleEvents = True, orderBy = "startTime"   )
        events = event_result.get("items", [])

        if not events:
            print("No upcocming events found!")
            return
        
        for event in events:
            start = event["start"].get("dataTime", event["start"]-get("date"))
            print(start, event["summary"])

    except HttpError as error:
        print("An error occurred: " , error)


def intiate_calendar(firebase_user_token):
    """
    Initialize Google Calendar API with Firebase User Token
    """
    try:
        # Authenticate the user with their Firebase token
        user = auth.verify_id_token(firebase_user_token)
        print(f"Authenticated Firebase user: {user['email']}")

        # Retrieve Google Calendar credentials for the user from the Firebase database
        google_calendar_creds = db.child("peers").child(user['uid']).child("GOOGLE_CREDENTIALS").get().val()

        if not google_calendar_creds:
            # If no credentials exist, start the Google Calendar OAuth flow
            print("Google Calendar credentials not found. Initiating OAuth flow...")
            flow = InstalledAppFlow.from_client_secrets_file(os.getenv('GOOGLE_CREDENTIALS'), SCOPES)
            cred_google_calendar = flow.run_local_server(port=0)

            # Save credentials to Firebase database
            db.child("peers").child(user['uid']).update({
                "google_calendar_creds": cred_google_calendar.to_json()
            })
            return cred_google_calendar

        else:
            # Load credentials from Firebase database
            cred_google_calendar = Credentials.from_authorized_user_info(google_calendar_creds, SCOPES)
            print("Google Calendar credentials loaded successfully.")
            return cred_google_calendar

    except Exception as error:
        print(f"An error occurred during Google Calendar authentication: {error}")
        return None


def get_calendar(firebase_user_token):
    """
    Retrieve Google Calendar events for a user authenticated via Firebase.
    """
    try:
        creds = intiate_calendar(firebase_user_token)
        if not creds:
            print("Unable to retrieve Google Calendar credentials.")
            return

        # Use the credentials to access Google Calendar API
        service = build('calendar', 'v3', credentials=creds)
        now = dt.datetime.utcnow().isoformat() + 'Z'
        print(f"Fetching events from Google Calendar starting from {now}...")
        
        events_result = service.events().list(
            calendarId='primary', timeMin=now,
            maxResults=10,singleEvents=True,
            orderBy='startTime'
        ).execute()

        events = events_result.get('items', [])
        if not events:
            print("No upcoming events found.")
        else:
            print("Upcoming events:")
            for event in events:
                start = event['start'].get('dateTime', event['start'].get('date'))
                print(start, event['summary'])

    except Exception as error:
        print(f"An error occurred: {error}")


def create_calendar_event(firebase_user_token):
    """
    Create a new Google Calendar event for a user authenticated via Firebase.
    """
    try:
        creds = intiate_google_calendar_with_firebase(firebase_user_token)
        if not creds:
            print("Unable to retrieve Google Calendar credentials.")
            return

        # Use the credentials to access Google Calendar API
        service = build('calendar', 'v3', credentials=creds)

        event = {
            'summary': 'Test Event',
            'location': 'Online',
            'description': 'This is a test event.',
            'start': {
                'dateTime': '2021-10-10T09:00:00-07:00',
                'timeZone': 'America/Los_Angeles',
            },
            'end': {
                'dateTime': '2021-10-10T17:00:00-07:00',
                'timeZone': 'America/Los_Angeles',
            },
            'attendees': [
                {'email': 'djsunshineofficial@gmail.com'},	
            ], 
        }

        event = service.events().insert(calendarId='primary', body=event).execute()
        print(f"Event created: {event.get('htmlLink')}")

    except Exception as error:
        print(f"An error occurred: {error}")

if __name__ and "__main__":
    main()