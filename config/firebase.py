import os
import json
import firebase_admin
from firebase_admin import credentials

firebase_creds = os.getenv("FIREBASE_CREDENTIALS")

if firebase_creds and not firebase_admin._apps:
    cred_dict = json.loads(firebase_creds)
    cred = credentials.Certificate(cred_dict)
    firebase_admin.initialize_app(cred)
