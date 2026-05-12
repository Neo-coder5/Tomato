from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics
from rest_framework.permissions import IsAuthenticated

from .models import Analysis
from .serializers import AnalysisSerializer, AnalyzeRequestSerializer
from .services.gemini import analyze_image
from .services.image import validate_image


class AnalyzeView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = AnalyzeRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        image_file = serializer.validated_data['image']
        validate_image(image_file)

        # Gemini tahlili
        result = analyze_image(image_file)

        # DB ga saqlash
        analysis = Analysis.objects.create(
            user=request.user,
            filename=image_file.name,
            kasallik_nomi=result.get('kasallik_nomi', ''),
            ishonch_darajasi=result.get('ishonch_darajasi', ''),
            sababi=result.get('sababi', ''),
            belgilari=result.get('belgilari', []),
            davolash=result.get('davolash', []),
            oldini_olish=result.get('oldini_olish', []),
            shoshilinchlik=result.get('shoshilinchlik', ''),
        )

        return Response(
            AnalysisSerializer(analysis).data,
            status=status.HTTP_201_CREATED
        )


class AnalysisHistoryView(generics.ListAPIView):
    serializer_class = AnalysisSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Analysis.objects.filter(user=self.request.user)


class AnalysisDetailView(generics.RetrieveAPIView):
    serializer_class = AnalysisSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Analysis.objects.filter(user=self.request.user)