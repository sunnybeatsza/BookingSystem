from firebase_config import auth_client, firebase_client, intialize_firebase,auth
import bcrypt
import firebase
from firebase import Firebase

intialize_firebase()
def register_user(name, email, passsword, role):

    try:
        user = auth_client.create_user(
            email = email,
            password = passsword 
        )

        user_ref = firebase_client.collection('users').document(user.uid)
        stuff = user_ref.get()
        user_ref.set({
            'name': name,
            'email': email,
            'role': role
        })
        print(f"User {name} registered successfully with email: {email}")
      

    except Exception as e:
        print(f"Error occured: {e}")

# register_user("Sean", "tksean7@gmail.com", "12345abc", "mentor")
# register_user("David", "davidmalan@gmail.com", 'david7@malan',"mentor")
# register_user("Tumisho", "tumi45@gmail.com", "tumisho45$", "peer")
# register_user("Cwengi", "acwengile@gmail.com", "cwengiadmin2", "mentor")


def verify_password(stored_hash, password):
    return bcrypt.checkpw(password.encode('utf-8'), stored_hash)


def login_user(email, password):
    try:
       
        firebase_config = {
            # Your Firebase configuration details here
            'apiKey': "AIzaSyBlcvae2_BEgcGBUbLWrLjIgqvLtrLrCQY",
            'authDomain': 'skillssync-ebaa9.firebaseapp.com',
            'databaseURL': 'https://skillssync-ebaa9.firebaseio.com',
            'projectId': 'skillssync-ebaa9',
            'storageBucket': '337287691485',
            'messagingSenderId': "1:337287691485:web:bcfd399d50a9decb6a6f34",
            'appId': "G-PG9HQ8ZDVV",
        }
        
        firebase = Firebase(firebase_config)
        auth = firebase.auth()
        
        user = auth.sign_in_with_email_and_password(email, password)
        
        print(f"User logged in successfully. UID: {user['localId']}, Email: {email}")

    except Exception as e:
        print(f"Error occurred: {e}")





login_user("kemboseattn7@gmail.com","123465753455555425rreeabc")

