import firebase_admin
from firebase_admin import credentials, auth, firestore


credentials_file = credentials.Certificate(r"C:\Users\User\Downloads\skillssync-ebaa9-firebase-adminsdk-ap0rz-3ed4e67283.json")
firebase_admin.initialize_app(credentials_file)

db = firestore.client()

def register_user(name, email, passsword, role):

    try:
        user = auth.create_user(
            email = email,
            password = passsword 
        )

        user_ref = db.collection('users').document(user.uid)
        user_ref.set({
            'name': name,
            'email': email,
            'role': role
        })
        print(f"User {name} registered successfully with email: {email}")

    except Exception as e:
        print(f"Error occured: {e}")


register_user("Sean", "tksean7@gmail.com", "12345abc", "mentor")