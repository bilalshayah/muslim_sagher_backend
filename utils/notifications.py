from firebase_admin import messaging
from config.firebase import init_firebase


def send_firebase_notification(token, title, body, data=None):
    """Send a Firebase push notification. No-op if FIREBASE_CREDENTIALS is not set."""
    if not init_firebase():
        return {"success": False, "reason": "FIREBASE_CREDENTIALS not configured"}

    message = messaging.Message(
        notification=messaging.Notification(
            title=title,
            body=body,
        ),
        token=token,
        data=data or {}
    )

    response = messaging.send(message)
    return {"success": True, "response": response}