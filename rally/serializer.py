from rest_framework import serializers
from .models import FantasyTeamRally, Piloto, Copiloto, Coche, ParticipacionRally

class PilotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Piloto
        fields = ('id', 'nombre', 'bandera', 'precio', 'puntos_totales')


class CopilotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Copiloto
        fields = ('id', 'nombre', 'bandera', 'precio', 'puntos_totales')


class CocheSerializer(serializers.ModelSerializer):
    class Meta:
        model = Coche
        fields = ('id', 'modelo', 'imagen', 'precio', 'puntos_totales')


class FantasyTeamRallySerializer(serializers.ModelSerializer):
    # Aquí usamos los serializers completos en lugar de los IDs
    pilotos = PilotoSerializer(many=True, read_only=True)
    copilotos = CopilotoSerializer(many=True, read_only=True)
    coches = CocheSerializer(many=True, read_only=True)

    # Para updates, necesitamos campos adicionales de solo escritura
    piloto_ids = serializers.PrimaryKeyRelatedField(
        many=True, write_only=True, queryset=Piloto.objects.all(), source='pilotos'
    )
    copiloto_ids = serializers.PrimaryKeyRelatedField(
        many=True, write_only=True, queryset=Copiloto.objects.all(), source='copilotos'
    )
    coche_ids = serializers.PrimaryKeyRelatedField(
        many=True, write_only=True, queryset=Coche.objects.all(), source='coches'
    )

    rally_nombre = serializers.CharField(source='rally.nombre', read_only=True)
    user_username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = FantasyTeamRally
        fields = (
            'id', 'user', 'user_username', 'rally', 'rally_nombre',
            'pilotos', 'copilotos', 'coches', 'puntos',
            'piloto_ids', 'copiloto_ids', 'coche_ids',
        )


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
