import pyrebase
import argparse
import os
from dotenv import load_dotenv
import firebase_admin
import datetime as dt
from firebase_admin import credentials,auth

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SCOPES = ["https://www.googleapis.com/auth/calendar"]


load_dotenv()  # Load environment variables from .env file


cred = credentials.Certificate(os.getenv("CREDENTIALS"))
firebase_admin.initialize_app(cred)
config = {
    "apiKey": os.getenv("FIREBASE_API_KEY"),
    "authDomain": os.getenv("FIREBASE_AUTH_DOMAIN"),
    "databaseURL": os.getenv("FIREBASE_DATABASE_URL"),
    "storageBucket": os.getenv("FIREBASE_STORAGE_BUCKET"),
}

firebase = pyrebase.initialize_app(config)

pyrebase_auth = firebase.auth()
db = firebase.database()

# Set custom claim (isAdmin)
def set_admin_role(uid):
    auth.set_custom_user_claims(uid, {"isAdmin": True})



def login():
    email = input("Enter your email: ")
    password = input("Enter your password: ")
    print(f"Logging in with email: {email}")
    try:  
        user = pyrebase_auth.sign_in_with_email_and_password(email, password)
        user_token = user['idToken']
        with open("user_token.txt", "w") as file:
            file.write(user_token)
        return user_token
    except Exception as error:
        print(f"There was an error: {error}")
        return None

def signup():
    email = input("Enter your email: ")
    password = input("Create a password: ")
    name = input("Please enter your name: ")
    role = input("Are you a peer or mentor: ")
    username = input("Please create a username: ")

    print(f"Signing up with email: {email}")
    print("Sign up successful!")

    try:
      pyrebase_auth.create_user_with_email_and_password(email,password)
      data = {"email": email,
              "password":password,
              "role":role,
              "username":username,
              "name":name,
              "staus":"availabe",
              }
      
      if role == "peer": 
        db.child("peers").push(data)
      elif role == "mentor":
          db.child("mentors").push(data)

    except Exception as error:
        print(f"There was an error: {error}")

def intiate_google_calendar_with_firebase(firebase_user_token):
    """
    Initialize Google Calendar API with Firebase User Token
    """
    try:
        # Authenticate the user with their Firebase token
        user = auth.verify_id_token(firebase_user_token)
        print(f"Authenticated Firebase user: {user['email']}")

        # Retrieve Google Calendar credentials for the user from the Firebase database
        google_calendar_creds = db.child("peers").child(user['uid']).child("google_calendar_creds").get().val()

        if not google_calendar_creds:
            # If no credentials exist, start the Google Calendar OAuth flow
            print("Google Calendar credentials not found. Initiating OAuth flow...")
            flow = InstalledAppFlow.from_client_secrets_file('GOOGLE_CREDENTIALS', SCOPES)
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


def get_calendar_events_with_firebase(firebase_user_token):
    """
    Retrieve Google Calendar events for a user authenticated via Firebase.
    """
    try:
        creds = intiate_google_calendar_with_firebase(firebase_user_token)
        if not creds:
            print("Unable to retrieve Google Calendar credentials.")
            return

        # Use the credentials to access Google Calendar API
        service = build('calendar', 'v3', credentials=creds)
        now = dt.datetime.utcnow().isoformat() + 'Z'
        print(f"Fetching events from Google Calendar starting from {now}...")
        
        events_result = service.events().list(
            calendarId='primary', timeMin=now,
            maxResults=10, singleEvents=True,
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


def create_calendar_event_with_firebase(firebase_user_token):
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

def main():
    parser = argparse.ArgumentParser(description="Authentication.")
    subparsers = parser.add_subparsers(dest="command")

    # Login command
    subparsers.add_parser("login", help="login to your account")

    # Signup command
    subparsers.add_parser("signup", help="sign up using email and password")

    # Get calendar events command
    subparsers.add_parser("get_calendar_events", help="get upcoming calendar events")

    # Create calendar event command
    subparsers.add_parser("create_calendar_event", help="create a new calendar event")

    args = parser.parse_args()
    
    if args.command == "login":
        firebase_user_token = login()
        if firebase_user_token:
            print("Login successful. Token acquired.")
    elif args.command == "signup":
        signup()
    else:
        if args.command == "get_calendar_events":
            with open("user_token.txt", "r") as file:
                firebase_user_token = file.read()
            if firebase_user_token:
                get_calendar_events_with_firebase(firebase_user_token)
        elif args.command == "create_calendar_event":
            if firebase_user_token:
                create_calendar_event_with_firebase(firebase_user_token)
        else:
            parser.print_help()


if __name__ == "__main__":
    main()
