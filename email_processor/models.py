from django.db import models

class Email(models.Model):
    sender = models.CharField(max_length=255)
    subject = models.CharField(max_length=255)
    body = models.TextField()
    date_received = models.DateTimeField()
    
    # AI fields
    summary = models.TextField(blank=True, null=True)
    sentiment = models.CharField(max_length=50, blank=True, null=True) # positive, negative, neutral
    
    def __str__(self):
        return f"{self.subject} - {self.sender}"