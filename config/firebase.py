# import os
# import json
# import firebase_admin
# from firebase_admin import credentials

# firebase_creds = os.getenv("FIREBASE_CREDENTIALS")

# if firebase_creds and not firebase_admin._apps:
#     cred_dict = json.loads(firebase_creds)
#     cred = credentials.Certificate(cred_dict)
#     firebase_admin.initialize_app(cred)
# config/firebase.py
import os
import json
import logging
import firebase_admin
from firebase_admin import credentials

logger = logging.getLogger(__name__)


def init_firebase():
    """Initialize Firebase if FIREBASE_CREDENTIALS is set. Returns True if initialized, False otherwise."""
    if firebase_admin._apps:
        return True

    firebase_creds = os.getenv("FIREBASE_CREDENTIALS")
    if not firebase_creds or not firebase_creds.strip():
        return False

    try:
        # يدعم JSON على سطر واحد أو متعدد (مهم: على Railway يجب سطر واحد)
        cred_dict = json.loads(firebase_creds)
        cred = credentials.Certificate(cred_dict)
        firebase_admin.initialize_app(cred)
        return True
    except json.JSONDecodeError as e:
        logger.warning("FIREBASE_CREDENTIALS: JSON غير صالح - تأكد أن القيمة سطر واحد (minified). %s", e)
        return False
    except Exception as e:
        logger.warning("FIREBASE_CREDENTIALS: فشل تهيئة Firebase: %s", e)
        return False