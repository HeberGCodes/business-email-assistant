from celery import shared_task, chain
from .fetch_emails import fetch_emails
from .models import Email
from .ai_tasks import summarize_and_analyze_email

@shared_task
def fetch_emails_task():
    """
    1. Fetch unread emails from Gmail and save them to the database.
    2. For each new email, chain AI processing to summarize and analyze the email.
    """
    new_email_ids = fetch_emails() # Fetch new emails and get their IDs

    for e_id in new_email_ids:
        # Create a chain so each email is processed by the AI after fetching
        chain(
            summarize_and_analyze_email.s(e_id)
        )()
        
    return f"Fetched {len(new_email_ids)} new emails and scheduled AI tasks"

