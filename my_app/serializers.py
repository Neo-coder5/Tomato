from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Analysis, Plant, Disease


class RegisterSerializer(serializers.ModelSerializer):
    """Yangi foydalanuvchi ro'yxatdan o'tish"""
    password  = serializers.CharField(write_only=True, min_length=8)
    password2 = serializers.CharField(write_only=True)

    class Meta:
        model  = User
        fields = ['username', 'email', 'password', 'password2']

    def validate(self, data):
        if data['password'] != data['password2']:
            raise serializers.ValidationError("Parollar mos kelmaydi")
        return data

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Bu email allaqachon ro'yxatdan o'tgan")
        return value

    def create(self, validated_data):
        validated_data.pop('password2')
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            password=validated_data['password'],
        )
        return user


class PlantSerializer(serializers.ModelSerializer):
    """O'simlik ma'lumotlari"""

    class Meta:
        model  = Plant
        fields = ['id', 'name_uz', 'name_ru', 'name_latin', 'description']


class DiseaseSerializer(serializers.ModelSerializer):
    """Kasallik ma'lumotlari"""
    plant_name = serializers.CharField(source='plant.name_uz', read_only=True)

    class Meta:
        model  = Disease
        fields = [
            'id', 'name', 'plant_name', 'description',
            'severity', 'symptoms', 'treatment', 'prevention'
        ]


class AnalysisSerializer(serializers.ModelSerializer):
    """Tahlil natijasi — foydalanuvchiga qaytariladigan ma'lumot"""
    username     = serializers.CharField(source='user.username', read_only=True)
    plant_name   = serializers.CharField(source='plant.name_uz', read_only=True)
    disease_name = serializers.CharField(source='disease.name',  read_only=True)

    # raw_result ichidan chiqarib ko'rsatamiz
    kasallik_nomi    = serializers.SerializerMethodField()
    ishonch_darajasi = serializers.SerializerMethodField()
    sababi           = serializers.SerializerMethodField()
    belgilari        = serializers.SerializerMethodField()
    davolash         = serializers.SerializerMethodField()
    oldini_olish     = serializers.SerializerMethodField()
    shoshilinchlik   = serializers.SerializerMethodField()

    class Meta:
        model  = Analysis
        fields = [
            'id', 'username', 'image', 'status', 'is_healthy', 'confidence',
            'plant_name', 'disease_name',
            # Gemini natijalari
            'kasallik_nomi', 'ishonch_darajasi', 'sababi',
            'belgilari', 'davolash', 'oldini_olish', 'shoshilinchlik',
            # Texnik
            'error_message', 'created_at',
        ]

    def get_kasallik_nomi(self, obj):
        return obj.raw_result.get('kasallik_nomi', '')

    def get_ishonch_darajasi(self, obj):
        return obj.raw_result.get('ishonch_darajasi', '')

    def get_sababi(self, obj):
        return obj.raw_result.get('sababi', '')

    def get_belgilari(self, obj):
        return obj.raw_result.get('belgilari', [])

    def get_davolash(self, obj):
        return obj.raw_result.get('davolash', [])

    def get_oldini_olish(self, obj):
        return obj.raw_result.get('oldini_olish', [])

    def get_shoshilinchlik(self, obj):
        return obj.raw_result.get('shoshilinchlik', '')


class AnalyzeRequestSerializer(serializers.Serializer):
    """Foydalanuvchidan keladigan so'rov — faqat rasm"""
    image = serializers.ImageField()

    def validate_image(self, value):
        allowed_types = ['image/jpeg', 'image/png', 'image/webp']
        max_size      = 10 * 1024 * 1024  # 10MB

        if value.content_type not in allowed_types:
            raise serializers.ValidationError(
                "Faqat JPEG, PNG, WEBP formatlar qabul qilinadi"
            )
        if value.size > max_size:
            raise serializers.ValidationError(
                "Rasm 10MB dan kichik bo'lishi kerak"
            )
        return value