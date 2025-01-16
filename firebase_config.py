import firebase_admin
from firebase_admin import credentials, auth, firestore

def intialize_firebase():
    credentials_file = credentials.Certificate(r"C:\Users\User\Downloads\skillssync-ebaa9-firebase-adminsdk-ap0rz-3ed4e67283.json")
    firebase_admin.initialize_app(credentials_file)

def firebase_client():
    return firestore.client()

def auth_client():
    return auth