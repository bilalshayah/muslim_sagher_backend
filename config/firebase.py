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
    """Initialize Firebase. Reads from FIREBASE_CREDENTIALS_JSON or FIREBASE_CREDENTIALS (Railway recommends the first)."""
    if firebase_admin._apps:
        return True

    # Railway يوصي بـ FIREBASE_CREDENTIALS_JSON؛ ندعم الاثنين
    firebase_creds = os.getenv("FIREBASE_CREDENTIALS_JSON") or os.getenv("FIREBASE_CREDENTIALS")
    var_name = "FIREBASE_CREDENTIALS_JSON" if os.getenv("FIREBASE_CREDENTIALS_JSON") else "FIREBASE_CREDENTIALS"

    if firebase_creds is None:
        logger.warning("Firebase: المتغير غير موجود. أضف FIREBASE_CREDENTIALS_JSON أو FIREBASE_CREDENTIALS في Railway ثم Redeploy.")
        return False
    if not firebase_creds.strip():
        logger.warning("Firebase: القيمة فارغة (طول=%d). تحقق من القيمة في Variables.", len(firebase_creds))
        return False
    logger.info("Firebase: قراءة %s، طول القيمة = %d", var_name, len(firebase_creds))

    try:
        cred_dict = json.loads(firebase_creds)
        cred = credentials.Certificate(cred_dict)
        firebase_admin.initialize_app(cred)
        return True
    except json.JSONDecodeError as e:
        logger.warning("Firebase: JSON غير صالح. في Raw Editor استخدم سطر واحد (minified). %s", e)
        return False
    except Exception as e:
        logger.warning("Firebase: فشل التهيئة: %s", e)
        return False