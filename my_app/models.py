from django.db import models
from django.contrib.auth.models import User

class Person(models.Model):
    first_name = models.CharField(max_length=250)
    last_name = models.CharField(max_length=250)
    email = models.EmailField(max_length=250)
    company = models.CharField(max_length=250)
    phone = models.CharField(max_length=12)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class PredictionHistory(models.Model):
    """Foydalanuvchilar yuklagan rasmlar va AI tahlil natijalari tarixi"""
    # Foydalanuvchi tizimga kirmagan bo'lsa ham ishlatish uchun null=True qilamiz
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    image_name = models.CharField(max_length=255)
    detected_disease = models.CharField(max_length=150)
    confidence = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.image_name} - {self.detected_disease} ({self.confidence})"
