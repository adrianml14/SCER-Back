from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.exceptions import ValidationError

from rally.models import FantasyTeam
from .models import Liga, ParticipacionLiga
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework import generics
from .serializer import ClasificacionGeneralSerializer, LigaSerializer, ParticipacionLigaSerializer
from rest_framework.decorators import api_view
from django.db.models import Sum

User = get_user_model()

# Función ejemplo para detectar VIP (modifícala según tu modelo)
def es_vip(user):
    return user.roles.filter(nombre="VIP").exists()



class LigaListCreateView(generics.ListCreateAPIView):
    queryset = Liga.objects.all()
    serializer_class = LigaSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        user = self.request.user

        # ✅ Verifica si es VIP y ya tiene una liga
        if es_vip(user) and Liga.objects.filter(dueño=user).exists():
            raise ValidationError("Los usuarios VIP solo pueden crear una liga.")

        liga = serializer.save(dueño=user)
        ParticipacionLiga.objects.create(usuario=user, liga=liga)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

class ParticipacionLigaCreateView(generics.CreateAPIView):
    serializer_class = ParticipacionLigaSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        user = self.request.user

        # Limitar unión: usuario solo puede estar en una liga
        if ParticipacionLiga.objects.filter(usuario=user).exists():
            raise ValidationError("Solo puedes unirte a una liga.")

        serializer.save(usuario=user)


class MisLigasView(generics.ListAPIView):
    serializer_class = ParticipacionLigaSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return ParticipacionLiga.objects.filter(usuario=self.request.user)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context


class GestionParticipantesView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, liga_id):
        liga = get_object_or_404(Liga, id=liga_id)
        if not ParticipacionLiga.objects.filter(liga=liga).exists():
            return Response({'mensaje': 'No hay participantes en esta liga.'}, status=200)

        participantes = ParticipacionLiga.objects.filter(liga=liga)
        serializer = ParticipacionLigaSerializer(participantes, many=True)
        return Response(serializer.data, status=200)

    def post(self, request, liga_id):
        liga = get_object_or_404(Liga, id=liga_id)

        if liga.dueño != request.user:
            return Response({'error': 'No tienes permiso para gestionar esta liga.'}, status=403)

        username = request.data.get('username')
        usuario = get_object_or_404(User, username=username)

        # Verificar si usuario ya está en otra liga
        if ParticipacionLiga.objects.filter(usuario=usuario).exists():
            return Response({'error': 'El usuario ya pertenece a otra liga.'}, status=400)

        participacion, created = ParticipacionLiga.objects.get_or_create(usuario=usuario, liga=liga)
        if not created:
            return Response({'message': 'El usuario ya participa en la liga.'}, status=200)

        return Response({'message': 'Usuario añadido correctamente.'}, status=201)

    def delete(self, request, liga_id):
        liga = get_object_or_404(Liga, id=liga_id)

        if liga.dueño != request.user:
            return Response({'error': 'No tienes permiso para gestionar esta liga.'}, status=403)

        username = request.data.get('username')
        usuario = get_object_or_404(User, username=username)

        participacion = ParticipacionLiga.objects.filter(usuario=usuario, liga=liga).first()
        if not participacion:
            return Response({'error': 'El usuario no participa en esta liga.'}, status=404)

        participacion.delete()
        return Response({'message': 'Usuario eliminado correctamente.'}, status=200)


@api_view(['POST'])
def unirse_por_codigo(request):
    codigo = request.data.get('codigo')
    if not codigo:
        return Response({'error': 'Código requerido'}, status=400)

    try:
        liga = Liga.objects.get(codigo_unico=codigo)
    except Liga.DoesNotExist:
        return Response({'error': 'Código incorrecto'}, status=404)

    user = request.user

    # Verificar que el usuario no esté ya en una liga
    if ParticipacionLiga.objects.filter(usuario=user).exists():
        return Response({'error': 'Solo puedes unirte a una liga.'}, status=400)

    # Evitar duplicados (por si acaso)
    if ParticipacionLiga.objects.filter(usuario=user, liga=liga).exists():
        return Response({'mensaje': 'Ya estás en esta liga'}, status=200)

    ParticipacionLiga.objects.create(usuario=user, liga=liga)
    return Response({'mensaje': f'Te has unido a la liga "{liga.nombre}".'}, status=201)


class ClasificacionGeneralView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        clasificacion = (
            ParticipacionLiga.objects
            .values('usuario__id', 'usuario__username')
            .annotate(puntos_totales=Sum('puntos'))
            .order_by('-puntos_totales')
        )

        user_ids = [item['usuario__id'] for item in clasificacion]

        equipos = {e.user_id: e.nombre for e in FantasyTeam.objects.filter(user_id__in=user_ids)}

        clasificacion_formateada = [
            {
                'usuario': item['usuario__username'],
                'puntos_totales': item['puntos_totales'],
                'equipo_nombre': equipos.get(item['usuario__id'], 'Sin equipo')
            }
            for item in clasificacion
        ]

        serializer = ClasificacionGeneralSerializer(clasificacion_formateada, many=True)
        return Response(serializer.data)


class SalirDeLigaView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, liga_id):
        liga = get_object_or_404(Liga, id=liga_id)

        participacion = ParticipacionLiga.objects.filter(usuario=request.user, liga=liga).first()
        if not participacion:
            return Response({'error': 'No participas en esta liga.'}, status=404)

        participacion.delete()
        return Response({'mensaje': 'Has salido de la liga correctamente.'}, status=200)
