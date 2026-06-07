from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import (
    RegisterView,
    AnalyzeView,
    AnalysisHistoryView,
    AnalysisDetailView,
    PlantListView,
    DiseaseListView,
)

urlpatterns = [
    # Auth
    path('auth/register/', RegisterView.as_view(),       name='register'),
    path('auth/login/',    TokenObtainPairView.as_view(), name='login'),
    path('auth/refresh/',  TokenRefreshView.as_view(),    name='token_refresh'),

    # Tahlil
    path('analyze/',          AnalyzeView.as_view(),        name='analyze'),
    path('history/',          AnalysisHistoryView.as_view(), name='history'),
    path('history/<int:pk>/', AnalysisDetailView.as_view(),  name='detail'),

    # Ma'lumotnoma
    path('plants/',   PlantListView.as_view(),   name='plants'),
    path('diseases/', DiseaseListView.as_view(), name='diseases'),
]