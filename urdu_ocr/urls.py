from django.urls import path
from . import views

urlpatterns = [
    path('detect_text/', views.UrduOCRAPIView.as_view(), name='detect_text'),
]

# ./ngrok http 127.0.0.1:8989
