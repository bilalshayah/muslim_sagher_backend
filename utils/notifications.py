import logging
from firebase_admin import messaging
from config.firebase import init_firebase

logger = logging.getLogger(__name__)


def send_firebase_notification(token, title, body, data=None):
    """Send a Firebase push notification. No-op if FIREBASE_CREDENTIALS is not set."""
    if not init_firebase():
        logger.warning("Firebase: لم يتم إرسال الإشعار - FIREBASE_CREDENTIALS غير مضبوط أو غير صالح.")
        return {"success": False, "reason": "FIREBASE_CREDENTIALS not configured"}

    if not token or not token.strip():
        logger.warning("Firebase: لم يتم إرسال الإشعار - device_token فارغ.")
        return {"success": False, "reason": "empty token"}

    message = messaging.Message(
        notification=messaging.Notification(
            title=title,
            body=body,
        ),
        token=token,
        data=data or {}
    )

    try:
        response = messaging.send(message)
        logger.info("Firebase: تم إرسال الإشعار بنجاح، message_id=%s", response)
        return {"success": True, "response": response}
    except Exception as e:
        logger.exception("Firebase: فشل إرسال الإشعار: %s", e)
        return {"success": False, "reason": str(e)}