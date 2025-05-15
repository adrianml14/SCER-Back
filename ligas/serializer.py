from rest_framework import serializers
from .models import Liga, ParticipacionLiga
from django.contrib.auth import get_user_model
from rally.models import FantasyTeam 

User = get_user_model()

class LigaSerializer(serializers.ModelSerializer):
    dueño = serializers.ReadOnlyField(source='dueño.username')
    num_participantes = serializers.SerializerMethodField()
    codigo_unico = serializers.CharField(read_only=True)

    class Meta:
        model = Liga
        fields = ['id', 'nombre', 'dueño', 'fecha_creacion', 'num_participantes', 'codigo_unico']

    def get_num_participantes(self, obj):
        return obj.participantes.count()


class ParticipacionLigaSerializer(serializers.ModelSerializer):
    usuario = serializers.ReadOnlyField(source='usuario.username')
    liga_nombre = serializers.ReadOnlyField(source='liga.nombre')
    equipo_nombre = serializers.SerializerMethodField()  # Nuevo campo

    class Meta:
        model = ParticipacionLiga
        fields = ['id', 'usuario', 'liga', 'liga_nombre', 'equipo_nombre', 'fecha_union', 'puntos']

    def get_equipo_nombre(self, obj):
        try:
            return obj.usuario.fantasyteam.nombre
        except FantasyTeam.DoesNotExist:
            return "Sin equipo"


