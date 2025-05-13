from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from .models import Liga, ParticipacionLiga
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions
from .models import Liga, ParticipacionLiga
from .serializer import LigaSerializer, ParticipacionLigaSerializer
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework import status

class LigaListCreateView(generics.ListCreateAPIView):
    queryset = Liga.objects.all()
    serializer_class = LigaSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        liga = serializer.save(dueño=self.request.user)
        # Añadir al dueño como participante automáticamente
        ParticipacionLiga.objects.create(usuario=self.request.user, liga=liga)

class ParticipacionLigaCreateView(generics.CreateAPIView):
    serializer_class = ParticipacionLigaSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(usuario=self.request.user)

class MisLigasView(generics.ListAPIView):
    serializer_class = ParticipacionLigaSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return ParticipacionLiga.objects.filter(usuario=self.request.user)



User = get_user_model()

class GestionParticipantesView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, liga_id):
        """Añadir usuario a una liga (solo dueño)"""
        liga = get_object_or_404(Liga, id=liga_id)

        if liga.dueño != request.user:
            return Response({'error': 'No tienes permiso para gestionar esta liga.'}, status=403)

        username = request.data.get('username')
        usuario = get_object_or_404(User, username=username)

        participacion, created = ParticipacionLiga.objects.get_or_create(usuario=usuario, liga=liga)
        if not created:
            return Response({'message': 'El usuario ya participa en la liga.'}, status=200)

        return Response({'message': 'Usuario añadido correctamente.'}, status=201)

    def delete(self, request, liga_id):
        """Eliminar usuario de una liga (solo dueño)"""
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
        return Response({'error': 'Liga no encontrada con ese código'}, status=404)

    # Evitar duplicados
    if ParticipacionLiga.objects.filter(usuario=request.user, liga=liga).exists():
        return Response({'mensaje': 'Ya estás en esta liga'}, status=200)

    ParticipacionLiga.objects.create(usuario=request.user, liga=liga)
    return Response({'mensaje': f'Te has unido a la liga "{liga.nombre}".'}, status=201)
