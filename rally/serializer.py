from rest_framework import serializers
from .models import Piloto, Copiloto, Coche

class PilotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Piloto
        fields = ('id', 'nombre', 'bandera', 'precio')  # si equipo está en el modelo

class CopilotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Copiloto
        fields = ('id', 'nombre', 'bandera', 'precio')

class CocheSerializer(serializers.ModelSerializer):
    class Meta:
        model = Coche
        fields = ('id', 'modelo', 'imagen', 'precio')
