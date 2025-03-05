import os
from openai import OpenAI
from dotenv import load_dotenv
from pathlib import Path
from celery import shared_task
from django.utils.timezone import now
from .models import Email

# Load environment variables
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env") # Load environment variables

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY")) # Set the OpenAI API key

@shared_task
def summarize_and_analyze_email(email_id):
    """
    Summarize the email and extract sentiment using OpenAI GPT.
    We'll parse a structured JSON response to seperate the summary and sentiment.
    """
    try:
        email_obj = Email.objects.get(id=email_id) # Get the email object
        prompt = f"""
        You are an AI assistant. Summmarize the following email in 1-2 sentences, then provide a sentiment label (positive, negative, neutral).
        Return your response in valid JSON format with the keys "summary" and "sentiment".
        
        EMAIL BODY:
        {email_obj.body}
        """
        
        # Call the ChatCompletion API
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt},
            ],
            max_tokens=200,
            temperature=0.7
        )
        
        content = response.choices[0].message["content"].strip() # Get the response content
        
        # Parse the structured JSON response
        import json
        try:
            parsed = json.loads(content)
            summary = parsed.get("summary", "No summary provided")
            sentiment = parsed.get("sentiment", "Unknown")
        except json.JSONDecodeError:
            # If the AI response is not valid JSON, store raw text
            summary = content
            sentiment = "Could not parse sentiment"
        
        # Update the Email object with the AI fields
        email_obj.summary = summary
        email_obj.sentiment = sentiment
        email_obj.save() # Save the updated Email object
        
        return f"Email {email_id} processed: {summary} | {sentiment}"
    
    except Email.DoesNotExist:
        return f"Email {email_id} not found"
    except Exception as e:
        return f"Error processing email {email_id}: {e}"