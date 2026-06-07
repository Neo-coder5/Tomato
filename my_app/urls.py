from django.urls import path
from .views import LeafDiseaseAnalyzeView, home_page_view  # <-- home_page qo'shildi

urlpatterns = [
    # Bosh sahifa: http://127.0.0.1:8000/
    path('', home_page_view, name='home'),

    # API manzili (Bunga HTML ichidagi JavaScript so'rov yuboradi)
    path('api/analyze-leaf/', LeafDiseaseAnalyzeView.as_view(), name='analyze-leaf'),
]