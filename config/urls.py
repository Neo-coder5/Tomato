from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),

    # Siz ochgan app'ingiz ichidagi urls.py faylini ulash
    # (Agar app nomi 'app' bo'lsa, quyidagicha bo'ladi)
    path('', include('my_app.urls')),
]

# Media fayllarni (rasmlarni) Django rivojlanish (development) rejimida o'qiy olishi uchun
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)