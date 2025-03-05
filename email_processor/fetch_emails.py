import os
import imaplib
import email
from email.header import decode_header
from pathlib import Path
from dotenv import load_dotenv
from django.utils.timezone import now
from email_processor.models import Email

# Load environment variables
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

# IMAP settings
IMAP_SERVER = os.getenv("IMAP_SERVER", "imap.gmail.com")
IMAP_PORT = int(os.getenv("IMAP_PORT", 993))
EMAIL_ACCOUNT = os.getenv("EMAIL_ACCOUNT") 
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD") 

def decode_mime_words(value):
    """Safely decode MIME encoded words in email headers to str"""
    decoded_parts = decode_header(value)
    return ''.join([
        part.decode(encoding or 'utf-8') if isinstance(part, bytes) else part
        for part, encoding in decoded_parts
    ])

def fetch_emails():
    """
    Fetches UNSEEN emails from your IMAP inbox, stores them in the Email model,
    and returns a list of the newly created Email object IDs.
    """
    
    new_ids = [] # List to store the IDs of new emails
    
    try:
        # Connect to Gmail IMAP server
        mail = imaplib.IMAP4_SSL(IMAP_SERVER, IMAP_PORT)
        mail.login(EMAIL_ACCOUNT, EMAIL_PASSWORD)
        
        mail.select('inbox') # Select the inbox folder
        
        # Search for all unread emails
        status, messages = mail.search(None, 'UNSEEN') 
        email_ids = messages[0].split() # Get the email ids
        
        print(f"Found {len(email_ids)} new emails") # Print the number of emails found
        
        for email_id in email_ids:
            # fetch the email by ID
            status, message = mail.fetch(email_id, '(RFC822)')
            raw_email = message[0][1] # Get the raw email message
            
            # Convert the raw email message to a Python object (parse the email content)
            msg = email.message_from_bytes(raw_email)
            
            # Decode the email subject safely
            subject = decode_mime_words(msg.get("Subject")) if msg["Subject"] else "No Subject"
                
            # Decode the email sender safely
            sender = decode_mime_words(msg.get("From")) if msg["From"] else "Unknown Sender"
                
            # Extract the email body (plaintext or HTML)
            body = ""
            if msg.is_multipart():
                for part in msg.walk():
                    content_type = part.get_content_type()
                    content_disposition = str(part.get("Content-Disposition"))
                    
                    if content_type == "text/plain" and "attachment" not in content_disposition:
                        body = part.get_payload(decode=True).decode("utf-8", errors="ignore")
                        break
            else:
                body = msg.get_payload(decode=True).decode("utf-8", errors="ignore")
                
            # Create the email object in the database
            email_obj = Email.objects.create(
                sender=sender,
                subject=subject,
                body=body,
                date_received=now()
            )
            
            # Append newly created email ID to the list
            new_ids.append(email_obj.id)
            
            print(f"Saved email: {subject} from {sender}")
            
        # Close IMAP connection
        mail.logout()
    
    except Exception as e:
        print(f"Error fetching emails: {e}")

    # Return the list of newly created email IDs
    return new_ids