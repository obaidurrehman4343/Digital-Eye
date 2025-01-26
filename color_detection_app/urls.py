from django.urls import path
from . import views

urlpatterns = [
    path('detect_color/', views.ColorDetectionAPIView.as_view(), name='detect_color'),
]
