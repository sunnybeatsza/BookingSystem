from firebase_config import firebase_client, intialize_firebase
from datetime import datetime
intialize_firebase()


#Fetch and display a list of available mentors
def get_mentors():
    try:
        user_ref = firebase_client().collection('users')
        users = user_ref.get()

        if users:
            for user in users:
                user_data = user.to_dict()
                if  user_data['role'] == 'peer':
                    print(f"Name: {user_data['name']}, Email: {user_data['email']}, Role: {user_data['role']}")
        else:
            print(f"No users found. ")


    
    except Exception as e:
        print(f"Error occured: {e}")



def book_mentor_session(user_email, mentor_email, session_time):
    try:
        mentor_ref = firebase_client().collection('users')
        mentor = mentor_ref.where("email", "==", mentor_email).get()
        
        if mentor:
            mentor_data = mentor[0].to_dict()
            mentor_name = mentor_data['email']
            
            
            session_ref = firebase_client().collection('sessions').add({
                'user_email': user_email,
                'mentor_id': mentor_email,
                'mentor_name': mentor_name,
                'session_time': session_time,
                'status': 'scheduled'
            })
            print(f"Session scheduled with {mentor_name} at {session_time}.")
        else:
            print("Mentor not found.")
    
    except Exception as e:
        print(f"Error occurred: {e}")

get_mentors()
book_mentor_session("kembosean7@gmail.com", "davidmalan@gmail.com","14:00")