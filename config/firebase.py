import firebase_admin
from firebase_admin import credentials

import os
from django.conf import settings

if not firebase_admin._apps:
    cred = credentials.Certificate(
        os.path.join(settings.BASE_DIR, "config/firebase-service-account.json")
    )
    firebase_admin.initialize_app(cred)