from django.db import models

# Create your models here.
from django.db import models


class PlantImage(models.Model):
    image = models.ImageField(upload_to='plants/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Plant {self.id}"