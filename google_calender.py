import os.path
import datetime as dt

from dotenv import load_dotenv
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import firebase_admin
import webbrowser
from firebase_admin import credentials,auth

import pyrebase
import os

load_dotenv()


config = {
    "apiKey": os.getenv("FIREBASE_API_KEY"),
    "authDomain": os.getenv("FIREBASE_AUTH_DOMAIN"),
    "databaseURL": os.getenv("FIREBASE_DATABASE_URL"),
    "storageBucket": os.getenv("FIREBASE_STORAGE_BUCKET"),
}


firebase = pyrebase.initialize_app(config)

pyrebase_auth = firebase.auth()

db = firebase.database()

SCOPES = [ "https://www.googleapis.com/auth/calendar.events"]

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

def get_session_data():
    """
    Retrieve session data from the user.
    # """
    # summary = input("Enter the event summary: ")
    # location = input("Enter the event location: ")
    # description = input("Enter the event description: ")
    # start_date = input("Enter the event start date (YYYY-MM-DD): ")
    # start_time = input("Enter the event start time (HH:MM): ")
    # end_date = input("Enter the event end date (YYYY-MM-DD): ")
    # end_time = input("Enter the event end time (HH:MM): ")

    #Generate sample data
    summary = "Mentor Session"  
    location = "Online"
    description = "Mentor session with mentor"
    start_date = "2025-01-24"
    start_time = "09:00"
    end_date = "2025-01-24"
    end_time = "10:00"


    session_data = {
    'summary': 'Google I/O 2015',
    'location': '800 Howard St., San Francisco, CA 94103',
    'description': 'A chance to hear more about Google\'s developer products.',
    'start': {
        'dateTime': '2025-01-28T09:00:00-07:00',
        'timeZone': 'America/Los_Angeles',
    },
    'end': {
        'dateTime': '2025-01-28T17:00:00-07:00',
        'timeZone': 'America/Los_Angeles',
    },
    'recurrence': [
        'RRULE:FREQ=DAILY;COUNT=2'
    ],
    'attendees': [
        {'email': 'makgerutumisho55@gmail.com'},
        {'email': 'momakgejhb024@student.wethinkcode.co.za'},
    ],
    'reminders': {
        'useDefault': False,
        'overrides': [
        {'method': 'email', 'minutes': 24 * 60},
        {'method': 'popup', 'minutes': 10},
        ],
    },
    }
    return session_data

def create_calendar_event(firebase_user_token, session_data):
    """
    Create a new Google Calendar event for a user authenticated via Firebase.
    """
    try:
        creds = intiate_calendar(firebase_user_token)
        if not creds:
            print("Unable to retrieve Google Calendar credentials.")
            return

        # Use the credentials to access Google Calendar API
        service = build('calendar', 'v3', credentials=creds)

        event = session_data

        event = service.events().insert(calendarId='primary', body=event).execute()
        print(f"Event created: {event.get('htmlLink')}")
        webbrowser.open(event.get('htmlLink'))

    except Exception as error:
        print(f"An error occurred: {error}")
