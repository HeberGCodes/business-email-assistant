from django.urls import path
from .views import EmailListAPIView

urlpatterns = [
    path('emails/', EmailListAPIView.as_view(), name='email-list'),
]

