from django.urls import path
from .views import PlantImageUploadAPIView

urlpatterns = [
    path('upload/', PlantImageUploadAPIView.as_view()),
]