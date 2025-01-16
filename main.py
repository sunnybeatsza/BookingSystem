import pyrebase
import argparse
import os
from dotenv import load_dotenv
import firebase_admin
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

auth = firebase.auth()
db = firebase.database()

# Set custom claim (isAdmin)
def set_admin_role(uid):
    auth.set_custom_user_claims(uid, {"isAdmin": True})



def login():
    email = input("Enter your email: ")
    password = input("Enter your password: ")
    print(f"Logging in with email: {email}")
    try:  
      auth.sign_in_with_email_and_password(email,password)
     
    except Exception as error:
        print(f"There was an error{error}")

def signup():
    email = input("Enter your email: ")
    password = input("Create a password: ")
    name = input("Please enter your name: ")
    role = input("Are you a peer or mentor: ")
    username = input("Please create a username: ")

    print(f"Signing up with email: {email}")
    print("Sign up successful!")
    try:
      auth.create_user_with_email_and_password(email,password)
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



def set_admin_user():
    pass



def main():
    parser = argparse.ArgumentParser(description="Authentication.")
    subparsers = parser.add_subparsers(dest="command")

    # Login command
    subparsers.add_parser("login", help="login to your account")

    # Signup command
    subparsers.add_parser("signup",help="sign up using email and passoword")

    args = parser.parse_args()

    if args.command == "login":
        login()
    elif args.command == "signup":
        signup()
    else:
        parser.print_help()


if __name__ =="__main__":
    main()