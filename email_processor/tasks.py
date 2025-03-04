from celery import shared_task
from .fetch_emails import fetch_emails

@shared_task
def fetch_emails_task():
    """
    Celery task to fetch emails from Gmail.
    """
    fetch_emails()
    return "Email fetching complete!"
