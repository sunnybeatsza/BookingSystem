import pyrebase
import argparse
import os
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

config = {
    "apiKey": os.getenv("FIREBASE_API_KEY"),
    "authDomain": os.getenv("FIREBASE_AUTH_DOMAIN"),
    "databaseURL": os.getenv("FIREBASE_DATABASE_URL"),
    "storageBucket": os.getenv("FIREBASE_STORAGE_BUCKET"),
}

firebase = pyrebase.initialize_app(config)

auth = firebase.auth()
db = firebase.database()

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
    print(f"Signing up with email: {email}")

    try:
      auth.create_user_with_email_and_password(email,password)

    except Exception as error:
        print(f"There was an error: {error}")


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