from django.db import models
from django.contrib.auth.models import User


class Plant(models.Model):
    """O'simlik turlari — ma'lumotnoma"""

    name_uz = models.CharField(max_length=100, verbose_name="Nomi (uz)")
    name_ru = models.CharField(max_length=100, verbose_name="Nomi (ru)", blank=True)
    name_latin = models.CharField(max_length=100, verbose_name="Lotin nomi", blank=True)
    description = models.TextField(verbose_name="Tavsif", blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "O'simlik"
        verbose_name_plural = "O'simliklar"
        ordering = ['name_uz']

    def __str__(self):
        return self.name_uz


class Disease(models.Model):
    """Kasalliklar — ma'lumotnoma"""

    SEVERITY_CHOICES = [
        ('past', 'Past'),
        ('orta', "O'rta"),
        ('yuqori', 'Yuqori'),
        ('kritik', 'Kritik'),
    ]

    name = models.CharField(max_length=200, verbose_name="Kasallik nomi")
    plant = models.ForeignKey(
        Plant,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='diseases',
        verbose_name="O'simlik turi"
    )
    description = models.TextField(verbose_name="Tavsif", blank=True)
    severity = models.CharField(
        max_length=10,
        choices=SEVERITY_CHOICES,
        default='orta',
        verbose_name="Og'irlik darajasi"
    )
    symptoms = models.JSONField(default=list, verbose_name="Belgilari")
    treatment = models.JSONField(default=list, verbose_name="Davolash usullari")
    prevention = models.JSONField(default=list, verbose_name="Oldini olish")

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Kasallik"
        verbose_name_plural = "Kasalliklar"

    def __str__(self):
        return self.name


class Analysis(models.Model):
    """Foydalanuvchi yuborgan rasm tahlili"""

    STATUS_CHOICES = [
        ('pending', 'Kutilmoqda'),
        ('processing', 'Tahlil qilinmoqda'),
        ('done', 'Tayyor'),
        ('error', 'Xatolik'),
    ]

    CONFIDENCE_CHOICES = [
        ('past', 'Past'),
        ('orta', "O'rta"),
        ('yuqori', 'Yuqori'),
    ]

    # Asosiy ma'lumotlar
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='analyses',
        verbose_name="Foydalanuvchi"
    )
    image = models.ImageField(
        upload_to='analyses/%Y/%m/%d/',
        verbose_name="Rasm"
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name="Holat"
    )

    # Natijalar (Gemini dan keladi)
    plant = models.ForeignKey(
        Plant,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='analyses',
        verbose_name="Aniqlangan o'simlik"
    )
    disease = models.ForeignKey(
        Disease,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='analyses',
        verbose_name="Aniqlangan kasallik"
    )
    is_healthy = models.BooleanField(
        default=False,
        verbose_name="Sog'lom o'simlikmi?"
    )
    confidence = models.CharField(
        max_length=10,
        choices=CONFIDENCE_CHOICES,
        blank=True,
        verbose_name="Ishonch darajasi"
    )

    # Gemini raw natijasi (har doim saqlaymiz)
    raw_result = models.JSONField(
        default=dict,
        verbose_name="AI to'liq javobi"
    )
    error_message = models.TextField(
        blank=True,
        verbose_name="Xatolik xabari"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Tahlil"
        verbose_name_plural = "Tahlillar"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} — {self.created_at.strftime('%d.%m.%Y')}"

    def mark_done(self, result: dict):
        """Gemini natijasini modelga yozadi"""
        self.raw_result = result
        self.is_healthy = result.get('kasallik_nomi', '').lower() == "sog'lom o'simlik"
        self.confidence = result.get('ishonch_darajasi', 'orta')
        self.status = 'done'
        self.save()

    def mark_error(self, message: str):
        """Xatolik bo'lsa holatni yangilaydi"""
        self.error_message = message
        self.status = 'error'
        self.save()