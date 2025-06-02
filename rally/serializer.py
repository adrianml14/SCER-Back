from rest_framework import serializers
from .models import FantasyTeamRally, Piloto, Copiloto, Coche

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

class FantasyTeamRallySerializer(serializers.ModelSerializer):
    pilotos = serializers.PrimaryKeyRelatedField(many=True, queryset=Piloto.objects.all())
    copilotos = serializers.PrimaryKeyRelatedField(many=True, queryset=Copiloto.objects.all())
    coches = serializers.PrimaryKeyRelatedField(many=True, queryset=Coche.objects.all())

    rally_nombre = serializers.CharField(source='rally.nombre', read_only=True)
    user_username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = FantasyTeamRally
        fields = (
            'id', 'user', 'user_username', 'rally', 'rally_nombre',
            'pilotos', 'copilotos', 'coches', 'puntos'
        )


from .models import ParticipacionRally, Rally


class ParticipacionPilotoSerializer(serializers.ModelSerializer):
    piloto = PilotoSerializer(read_only=True)
    rally_nombre = serializers.CharField(source='rally.nombre', read_only=True)

    class Meta:
        model = ParticipacionRally
        fields = ('id', 'rally', 'rally_nombre', 'piloto', 'posicion', 'puntos')


class ParticipacionCopilotoSerializer(serializers.ModelSerializer):
    copiloto = CopilotoSerializer(read_only=True)
    rally_nombre = serializers.CharField(source='rally.nombre', read_only=True)

    class Meta:
        model = ParticipacionRally
        fields = ('id', 'rally', 'rally_nombre', 'copiloto', 'posicion', 'puntos')


class ParticipacionCocheSerializer(serializers.ModelSerializer):
    coche = CocheSerializer(read_only=True)
    rally_nombre = serializers.CharField(source='rally.nombre', read_only=True)

    class Meta:
        model = ParticipacionRally
        fields = ('id', 'rally', 'rally_nombre', 'coche', 'posicion', 'puntos')
