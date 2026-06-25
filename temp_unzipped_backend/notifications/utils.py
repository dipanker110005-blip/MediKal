from .models import Notification

def send_notification(user, title, body):
    """
    Utility function to create and save a database notification for a given user.
    """
    try:
        notification = Notification.objects.create(
            user=user,
            title=title,
            body=body
        )
        return notification
    except Exception as e:
        print(f"FAILED TO SEND NOTIFICATION: {e}")
        return None
