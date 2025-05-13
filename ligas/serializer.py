from rest_framework import serializers
from .models import Liga, ParticipacionLiga
from django.contrib.auth import get_user_model

User = get_user_model()

class LigaSerializer(serializers.ModelSerializer):
    dueño = serializers.ReadOnlyField(source='dueño.username')

    class Meta:
        model = Liga
        fields = ['id', 'nombre', 'dueño', 'fecha_creacion']

class ParticipacionLigaSerializer(serializers.ModelSerializer):
    usuario = serializers.ReadOnlyField(source='usuario.username')
    liga_nombre = serializers.ReadOnlyField(source='liga.nombre')

    class Meta:
        model = ParticipacionLiga
        fields = ['id', 'usuario', 'liga', 'liga_nombre', 'fecha_union', 'puntos']

    def validate(self, attrs):
        # Validar si el usuario ya está en la liga
        if ParticipacionLiga.objects.filter(usuario=attrs['usuario'], liga=attrs['liga']).exists():
            raise serializers.ValidationError("El usuario ya está en esta liga.")
        return attrs

