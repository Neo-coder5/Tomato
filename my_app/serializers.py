from rest_framework import serializers
from .models import PlantImage


class PlantImageSerializer(serializers.ModelSerializer):

    class Meta:
        model = PlantImage
        fields = '__all__'