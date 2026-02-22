from firebase_admin import messaging
from config.firebase import init_firebase

def send_firebase_notification(token, title, body, data=None):
    init_firebase()
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