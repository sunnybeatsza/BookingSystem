from datetime import datetime
import pyrebase
import os
from dotenv import load_dotenv

load_dotenv()

config = {
    "apiKey": os.getenv("FIREBASE_API_KEY"),
    "authDomain": os.getenv("FIREBASE_AUTH_DOMAIN"),
    "databaseURL": os.getenv("FIREBASE_DATABASE_URL"),
    "storageBucket": os.getenv("FIREBASE_STORAGE_BUCKET"),
    "serviceAccount":os.getenv("CREDENTIALS")
}



firebase = pyrebase.initialize_app(config)
db = firebase.database()

#Fetch and display a list of available mentors
def get_mentors():
    try:
        users = db.child("mentors").get()
        if users:
            for user in users:
                user_data = user.val()
                if  user_data['role'] == 'mentor':
                    print(f"Name: {user_data['name']}, Email: {user_data['email']}, Role: {user_data['role']}, Status: {user_data['status']}")
        else:
            print(f"No users found. ")

    except Exception as e:
        print(f"Error occured: {e}")



def book_mentor_session(user_email, mentor_email, session_time):
    try:
        mentors = db.child("mentors").order_by_child(user_email).equal_to(mentor_email).get()
        if mentors.each():
            for mentor in mentors.each():
                mentor_data = mentor.val()
                print(f"Mentor found: {mentor_data['name']}")
                session_time = datetime.utcnow().isoformat() + 'Z'
            data = {
                'user_email': user_email,
                'mentor_id': mentor_email,
                'session_time': session_time,
                'status': 'scheduled'
            }
            db.child("sessions").push(data)
            print(f"Session scheduled with {mentor_data['name']} at {session_time}.")
        else:
            print("Mentor not found.")
    
    except Exception as e:
        print(f"Error occurred: {e}")

