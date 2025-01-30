import pyrebase
import argparse
import os
import firebase_admin
import datetime as dt


from dotenv import load_dotenv
from google_calender import create_calendar_event, get_session_data, get_calendar,cancel_booking
from bookings import get_mentors, book_mentor_session
from firebase_admin import credentials,auth



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

def logout():
    print(f"Logging out...")
    try:
        os.remove("user_token.txt")
        print("Logout successful.")
    except Exception as error:
        print(f"There was an error: {error}")
def signup():
    email = input("Enter your email: ")
    password = input("Create a password: ")
    name = input("Please enter your name: ")
    role = input("Are you a peer or mentor: ")
    print(f"Signing up with email: {email}")

    try:
      pyrebase_auth.create_user_with_email_and_password(email,password)
      data = {"email": email,
              "password":password,
              "role":role,
              "name":name,
              "status":"availabe",
              }
      
      if role == "peer": 
        db.child("peers").push(data)
        print("Peer account created successfully.")
      elif role == "mentor":
        db.child("mentors").push(data)
        print("Mentor account created successfully.")

    except Exception as error:
        print(f"There was an error: {error}")



def main():
    firebase_user_token = None 
    parser = argparse.ArgumentParser(description="Authentication.")
    subparsers = parser.add_subparsers(dest="command")

    # Login command
    subparsers.add_parser("login", help="login to your account")

    # Logout command
    subparsers.add_parser("logout",help="Logout of the application")

    # Signup command
    subparsers.add_parser("signup", help="sign up using email and password")

    #View Bookings command
    subparsers.add_parser("view_bookings", help="view confirmed bookings")

    #Cancel Booking command
    subparsers.add_parser("cancel_booking",help="cancel a booking on the calendar")

    # Get calendar events command
    subparsers.add_parser("get_calendar_events", help="get upcoming calendar events")

    # Create calendar event command
    subparsers.add_parser("create_calendar_event", help="create a new calendar event")

    # Get available mentors
    subparsers.add_parser("get_mentors", help="get available mentors")

    args = parser.parse_args()
    
    if args.command == "login":
        firebase_user_token = login()
        if firebase_user_token:
            print("Login successful. Token acquired.")
    elif args.command == "signup":
        signup()
    else:
        if args.command == "get_calendar_events":
            if os.path.exists("user_token.txt"):
                with open("user_token.txt", "r") as file:
                    firebase_user_token = file.read()
                if firebase_user_token:
                    get_calendar(firebase_user_token)
                else:
                    print("Please login to view calendar events.")
            else:
                print("Please login to view calendar events.")
        elif args.command == "get_mentors":
            get_mentors()
        elif args.command == "create_calendar_event":
            with open("user_token.txt", "r") as file:
                firebase_user_token = file.read()
            if firebase_user_token:
                session_data = get_session_data()
                create_calendar_event(firebase_user_token, session_data)
            else:
                print("Please login to create a calendar event.")

        elif args.command == "logout":
            logout()	
        
        elif args.command == "cancel_booking":
            if os.path.exists("user_token.txt"):
                with open("user_token.txt", "r") as file:
                    firebase_user_token = file.read()
                if firebase_user_token:
                    event_id = input("Enter the event ID to cancel: ")
                    cancel_booking(firebase_user_token, event_id)
                else:
                    print("Please login to cancel a booking.")
            else:
                print("Please login to cancel a booking.")
        else:
            parser.print_help()

if __name__ == "__main__":
    main()