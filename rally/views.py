from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import FantasyTeam, FantasyTeamRally, ParticipacionRally, Piloto, Copiloto, Coche, Rally
from .serializer import (
    FantasyTeamRallySerializer,
    ParticipacionCocheSerializer,
    ParticipacionCopilotoSerializer,
    ParticipacionPilotoSerializer,
    PilotoSerializer,
    CopilotoSerializer,
    CocheSerializer,
)


# Listado de elementos base
class PilotoListView(generics.ListAPIView):
    queryset = Piloto.objects.all()
    serializer_class = PilotoSerializer

class CopilotoListView(generics.ListAPIView):
    queryset = Copiloto.objects.all()
    serializer_class = CopilotoSerializer

class CocheListView(generics.ListAPIView):
    queryset = Coche.objects.all()
    serializer_class = CocheSerializer


# Obtener presupuesto del equipo
class ObtenerPresupuestoView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            equipo = FantasyTeam.objects.get(user=request.user)
            return Response({'presupuesto': equipo.presupuesto})
        except FantasyTeam.DoesNotExist:
            return Response({'error': 'No se encontró el equipo'}, status=status.HTTP_404_NOT_FOUND)


# Obtener elementos del equipo del usuario
class MisPilotosView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            equipo = FantasyTeam.objects.get(user=request.user)
            serializer = PilotoSerializer(equipo.pilotos.all(), many=True)
            return Response(serializer.data)
        except FantasyTeam.DoesNotExist:
            return Response({'error': 'No se encontró el equipo fantasy'}, status=status.HTTP_404_NOT_FOUND)

class MisCopilotosView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            equipo = FantasyTeam.objects.get(user=request.user)
            serializer = CopilotoSerializer(equipo.copilotos.all(), many=True)
            return Response(serializer.data)
        except FantasyTeam.DoesNotExist:
            return Response({'error': 'No se encontró el equipo fantasy'}, status=status.HTTP_404_NOT_FOUND)

class MisCochesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            equipo = FantasyTeam.objects.get(user=request.user)
            serializer = CocheSerializer(equipo.coches.all(), many=True)
            return Response(serializer.data)
        except FantasyTeam.DoesNotExist:
            return Response({'error': 'No se encontró el equipo fantasy'}, status=status.HTTP_404_NOT_FOUND)


# Comprar y vender elementos del equipo
class ComprarElementoView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, tipo, id_elemento):
        user = request.user
        try:
            equipo = FantasyTeam.objects.get(user=user)

            if tipo == 'piloto':
                elemento = Piloto.objects.get(id=id_elemento)
                equipo.pilotos.add(elemento)
            elif tipo == 'copiloto':
                elemento = Copiloto.objects.get(id=id_elemento)
                equipo.copilotos.add(elemento)
            elif tipo == 'coche':
                elemento = Coche.objects.get(id=id_elemento)
                equipo.coches.add(elemento)
            else:
                return Response({'error': 'Tipo de elemento no válido'}, status=status.HTTP_400_BAD_REQUEST)

            if equipo.presupuesto < elemento.precio:
                return Response({'error': 'No tienes suficiente presupuesto'}, status=status.HTTP_400_BAD_REQUEST)

            equipo.presupuesto -= elemento.precio
            equipo.save()

            return Response({'mensaje': f'{tipo.capitalize()} comprado correctamente'})
        except FantasyTeam.DoesNotExist:
            return Response({'error': 'Equipo no encontrado'}, status=status.HTTP_404_NOT_FOUND)
        except (Piloto.DoesNotExist, Copiloto.DoesNotExist, Coche.DoesNotExist):
            return Response({'error': f'{tipo.capitalize()} no encontrado'}, status=status.HTTP_404_NOT_FOUND)


class VenderElementoView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, tipo, id_elemento):
        user = request.user
        try:
            equipo = FantasyTeam.objects.get(user=user)

            if tipo == 'piloto':
                elemento = Piloto.objects.get(id=id_elemento)
                equipo.pilotos.remove(elemento)
            elif tipo == 'copiloto':
                elemento = Copiloto.objects.get(id=id_elemento)
                equipo.copilotos.remove(elemento)
            elif tipo == 'coche':
                elemento = Coche.objects.get(id=id_elemento)
                equipo.coches.remove(elemento)
            else:
                return Response({'error': 'Tipo de elemento no válido'}, status=status.HTTP_400_BAD_REQUEST)

            equipo.presupuesto += elemento.precio
            equipo.save()

            return Response({'mensaje': f'{tipo.capitalize()} vendido correctamente'})
        except FantasyTeam.DoesNotExist:
            return Response({'error': 'Equipo no encontrado'}, status=status.HTTP_404_NOT_FOUND)
        except (Piloto.DoesNotExist, Copiloto.DoesNotExist, Coche.DoesNotExist):
            return Response({'error': f'{tipo.capitalize()} no encontrado'}, status=status.HTTP_404_NOT_FOUND)


# Nombre del equipo
class ObtenerNombreEquipoView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            equipo = FantasyTeam.objects.get(user=request.user)
            return Response({'nombre': equipo.nombre})
        except FantasyTeam.DoesNotExist:
            return Response({'error': 'Equipo no encontrado'}, status=status.HTTP_404_NOT_FOUND)

class CambiarNombreEquipoView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        nuevo_nombre = request.data.get("nombre_equipo")
        if not nuevo_nombre:
            return Response({'error': 'Debes proporcionar un nombre'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            equipo = FantasyTeam.objects.get(user=request.user)
            equipo.nombre = nuevo_nombre
            equipo.save()
            return Response({'mensaje': 'Nombre del equipo actualizado correctamente'})
        except FantasyTeam.DoesNotExist:
            return Response({'error': 'Equipo no encontrado'}, status=status.HTTP_404_NOT_FOUND)


# Equipos por rally
class MisEquiposPorRallyView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = FantasyTeamRallySerializer

    def get_queryset(self):
        return FantasyTeamRally.objects.filter(user=self.request.user).order_by('-rally__id')


class ActualizarEquipoRallyView(generics.UpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = FantasyTeamRallySerializer
    queryset = FantasyTeamRally.objects.all()

    def get_object(self):
        user = self.request.user
        rally_id = self.kwargs.get('rally_id')
        obj, created = FantasyTeamRally.objects.get_or_create(user=user, rally_id=rally_id)
        return obj

    def perform_update(self, serializer):
        serializer.save()
        serializer.instance.actualizar_puntos()


# Histórico de desempeño
class HistoricoPilotoView(generics.ListAPIView):
    serializer_class = ParticipacionPilotoSerializer

    def get_queryset(self):
        return ParticipacionRally.objects.filter(piloto__id=self.kwargs['piloto_id']).order_by('-rally__id')


class HistoricoCopilotoView(generics.ListAPIView):
    serializer_class = ParticipacionCopilotoSerializer

    def get_queryset(self):
        return ParticipacionRally.objects.filter(copiloto__id=self.kwargs['copiloto_id']).order_by('-rally__id')


class HistoricoCocheView(generics.ListAPIView):
    serializer_class = ParticipacionCocheSerializer

    def get_queryset(self):
        return ParticipacionRally.objects.filter(coche__id=self.kwargs['coche_id']).order_by('-rally__id')


class ClasificacionPorRallyView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        data = []
        rallies = Rally.objects.all().order_by('-id')

        for rally in rallies:
            participaciones = FantasyTeamRally.objects.filter(rally=rally).select_related('user').order_by('-puntos')
            items = [{
                'usuario': p.user.username,
                'puntos': p.puntos,
                'equipo_nombre': FantasyTeam.objects.get(user=p.user).nombre,
                'rally': rally.nombre
            } for p in participaciones]

            data.append({
                'rally': rally.nombre,
                'clasificacion': items
            })

        return Response(data)


class HistoricoUsuarioView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        equipos_rally = FantasyTeamRally.objects.filter(user=request.user).select_related('rally').order_by('-rally__id')
        data = [{
            'rally': equipo.rally.nombre,
            'fecha': equipo.rally.fecha,
            'puntos': equipo.puntos
        } for equipo in equipos_rally]

        return Response(data)
