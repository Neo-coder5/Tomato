from rest_framework import serializers
from .models import Analysis

class AnalysisSerializer(serializers.ModelSerializer):
    class Meta:
        model = Analysis
        fields = [
            'id', 'filename', 'kasallik_nomi', 'ishonch_darajasi',
            'sababi', 'belgilari', 'davolash', 'oldini_olish',
            'shoshilinchlik', 'created_at'
        ]
        read_only_fields = fields


class AnalyzeRequestSerializer(serializers.Serializer):
    image = serializers.ImageField()