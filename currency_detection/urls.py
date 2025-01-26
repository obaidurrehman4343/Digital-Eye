from django.urls import path
from . import views

urlpatterns = [
    path('detect_currency/', views.CurrencyDetectionAPIView.as_view(), name='detect_currency'),
]

# ./ngrok http 127.0.0.1:8989
