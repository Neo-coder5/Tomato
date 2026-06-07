from django.urls import path
from .views import PlantDiseasePredictView

urlpatterns = [
    # Postman yoki Frontenddan /api/predict/ manziliga so'rov kelganda View ishga tushadi
    path('predict/', PlantDiseasePredictView.as_view(), name='plant_predict'),
]
