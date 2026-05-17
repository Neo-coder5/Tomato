from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth.models import User

from .models import Analysis, Plant, Disease
from .serializers import (
    AnalysisSerializer,
    AnalyzeRequestSerializer,
    RegisterSerializer,
)
from .services.gemini import analyze_image
from .services.image import validate_image


class RegisterView(APIView):
    """Ro'yxatdan o'tish — token kerak emas"""
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(
            {'message': f"{user.username} muvaffaqiyatli ro'yxatdan o'tdi"},
            status=status.HTTP_201_CREATED
        )


class AnalyzeView(APIView):
    """Rasm yuborish va kasallikni aniqlash"""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = AnalyzeRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        image_file = serializer.validated_data['image']

        # Rasm validatsiya
        validate_image(image_file)

        # Analysis obyekti yaratamiz — status 'pending'
        analysis = Analysis.objects.create(
            user=request.user,
            image=image_file,
            status='pending'
        )

        try:
            # Gemini ga yuboramiz
            analysis.status = 'processing'
            analysis.save()

            result = analyze_image(image_file)

            # Natijani modelga yozamiz
            analysis.mark_done(result)

        except Exception as e:
            analysis.mark_error(str(e))
            return Response(
                {'error': 'Tahlil qilishda xatolik yuz berdi', 'detail': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        return Response(
            AnalysisSerializer(analysis).data,
            status=status.HTTP_201_CREATED
        )


class AnalysisHistoryView(generics.ListAPIView):
    """Foydalanuvchi tahlil tarixi"""
    serializer_class = AnalysisSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Analysis.objects.filter(user=self.request.user)


class AnalysisDetailView(generics.RetrieveAPIView):
    """Bitta tahlil natijasi"""
    serializer_class = AnalysisSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Analysis.objects.filter(user=self.request.user)


class PlantListView(generics.ListAPIView):
    """Barcha o'simliklar ro'yxati"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        plants = Plant.objects.all().values('id', 'name_uz', 'name_latin')
        return Response(list(plants))


class DiseaseListView(generics.ListAPIView):
    """Barcha kasalliklar ro'yxati"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        diseases = Disease.objects.all().values(
            'id', 'name', 'severity', 'plant__name_uz'
        )
        return Response(list(diseases))