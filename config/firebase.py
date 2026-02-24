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
    # تشخيص: هل المتغير يصل للتطبيق؟ (نطبع الطول فقط لأمان المفتاح)
    if firebase_creds is None:
        logger.warning("FIREBASE_CREDENTIALS: المتغير غير موجود في البيئة (None). جرّب Redeploy بعد حفظ Variables.")
        return False
    if not firebase_creds.strip():
        logger.warning("FIREBASE_CREDENTIALS: القيمة فارغة (طول=%d). تحقق من القيمة في Railway.", len(firebase_creds))
        return False
    logger.info("FIREBASE_CREDENTIALS: موجود، طول القيمة = %d", len(firebase_creds))

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