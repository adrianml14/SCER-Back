from rest_framework import serializers
from .models import Liga, ParticipacionLiga
from django.contrib.auth import get_user_model
from rally.models import FantasyTeam 

User = get_user_model()

class LigaSerializer(serializers.ModelSerializer):
    dueño = serializers.ReadOnlyField(source='dueño.username')
    num_participantes = serializers.SerializerMethodField()
    codigo_unico = serializers.SerializerMethodField()

    class Meta:
        model = Liga
        fields = ['id', 'nombre', 'dueño', 'fecha_creacion', 'num_participantes', 'codigo_unico']

    def get_num_participantes(self, obj):
        return obj.participantes.count()

    def get_codigo_unico(self, obj):
        request = self.context.get('request')
        if request and obj.dueño == request.user:
            return obj.codigo_unico
        return None


class ParticipacionLigaSerializer(serializers.ModelSerializer):
    usuario = serializers.ReadOnlyField(source='usuario.username')
    liga_nombre = serializers.ReadOnlyField(source='liga.nombre')
    codigo_unico = serializers.SerializerMethodField()
    equipo_nombre = serializers.SerializerMethodField()

    class Meta:
        model = ParticipacionLiga
        fields = [
            'id',
            'usuario',
            'liga',
            'liga_nombre',
            'codigo_unico',
            'equipo_nombre',
            'fecha_union',
            'puntos'
        ]

    def get_equipo_nombre(self, obj):
        try:
            return obj.usuario.fantasyteam.nombre
        except FantasyTeam.DoesNotExist:
            return "Sin equipo"

    def get_codigo_unico(self, obj):
        request = self.context.get('request')
        if request and obj.liga.dueño == request.user:
            return obj.liga.codigo_unico
        return None


class ClasificacionGeneralSerializer(serializers.Serializer):
    usuario = serializers.CharField()
    puntos_totales = serializers.IntegerField()
    equipo_nombre = serializers.CharField()