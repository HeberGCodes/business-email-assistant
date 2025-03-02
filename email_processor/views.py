from rest_framework import generics
from .models import Email
from .serializers import EmailSerializer

class EmailListAPIView(generics.ListCreateAPIView):
    """
    API endpoint to retrieve all stored emails or create a new email
    """
    queryset = Email.objects.all().order_by('-date_received') # newest emails first
    serializer_class = EmailSerializer