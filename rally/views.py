from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import FantasyTeamRally, ParticipacionRally, Piloto, Copiloto, Coche, FantasyTeam
from .serializer import FantasyTeamRallySerializer, ParticipacionCocheSerializer, ParticipacionCopilotoSerializer, ParticipacionPilotoSerializer, PilotoSerializer, CopilotoSerializer, CocheSerializer
from rest_framework import status
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required

class PilotoListView(generics.ListAPIView):
    queryset = Piloto.objects.all()
    serializer_class = PilotoSerializer

class CopilotoListView(generics.ListAPIView):
    queryset = Copiloto.objects.all()
    serializer_class = CopilotoSerializer

class CocheListView(generics.ListAPIView):
    queryset = Coche.objects.all()
    serializer_class = CocheSerializer


class ObtenerPresupuestoView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        try:
            equipo = FantasyTeam.objects.get(user=user)
            return Response({'presupuesto': equipo.presupuesto})
        except FantasyTeam.DoesNotExist:
            return Response({'error': 'No se encontró el equipo'}, status=status.HTTP_404_NOT_FOUND)


#vistas para devolver el equipo fantasy del usuario

class MisPilotosView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            equipo = FantasyTeam.objects.get(user=request.user)
            pilotos = equipo.pilotos.all()
            serializer = PilotoSerializer(pilotos, many=True)
            return Response(serializer.data)
        except FantasyTeam.DoesNotExist:
            return Response({'error': 'No se encontró el equipo fantasy'}, status=status.HTTP_404_NOT_FOUND)

class MisCopilotosView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            equipo = FantasyTeam.objects.get(user=request.user)
            copilotos = equipo.copilotos.all()
            serializer = CopilotoSerializer(copilotos, many=True)
            return Response(serializer.data)
        except FantasyTeam.DoesNotExist:
            return Response({'error': 'No se encontró el equipo fantasy'}, status=status.HTTP_404_NOT_FOUND)

class MisCochesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            equipo = FantasyTeam.objects.get(user=request.user)
            coches = equipo.coches.all()
            serializer = CocheSerializer(coches, many=True)
            return Response(serializer.data)
        except FantasyTeam.DoesNotExist:
            return Response({'error': 'No se encontró el equipo fantasy'}, status=status.HTTP_404_NOT_FOUND)
        
# comprar y vender, viva el libre mercado

class ComprarElementoView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, tipo, id_elemento):
        user = request.user

        try:
            equipo = FantasyTeam.objects.get(user=user)

            if tipo == 'piloto':
                elemento = Piloto.objects.get(id=id_elemento)
            elif tipo == 'copiloto':
                elemento = Copiloto.objects.get(id=id_elemento)
            elif tipo == 'coche':
                elemento = Coche.objects.get(id=id_elemento)
            else:
                return Response({'error': 'Tipo de elemento no válido'}, status=status.HTTP_400_BAD_REQUEST)

            if equipo.presupuesto < elemento.precio:
                return Response({'error': 'No tienes suficiente presupuesto'}, status=status.HTTP_400_BAD_REQUEST)

            equipo.presupuesto -= elemento.precio
            equipo.save()

            if tipo == 'piloto':
                equipo.pilotos.add(elemento)
            elif tipo == 'copiloto':
                equipo.copilotos.add(elemento)
            elif tipo == 'coche':
                equipo.coches.add(elemento)

            return Response({'mensaje': f'{tipo.capitalize()} comprado correctamente'}, status=status.HTTP_200_OK)

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

            # Dependiendo del tipo, buscamos el objeto a vender
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

            # Agregar el precio al presupuesto
            equipo.presupuesto += elemento.precio
            equipo.save()

            return Response({'mensaje': f'{tipo.capitalize()} vendido correctamente'}, status=status.HTTP_200_OK)

        except FantasyTeam.DoesNotExist:
            return Response({'error': 'Equipo no encontrado'}, status=status.HTTP_404_NOT_FOUND)
        except (Piloto.DoesNotExist, Copiloto.DoesNotExist, Coche.DoesNotExist):
            return Response({'error': f'{tipo.capitalize()} no encontrado'}, status=status.HTTP_404_NOT_FOUND)
        
  # nombre del equipo, cambiarlo y verlo            
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
        # El usuario sólo puede modificar su propio equipo para un rally específico
        user = self.request.user
        rally_id = self.kwargs.get('rally_id')
        obj, created = FantasyTeamRally.objects.get_or_create(user=user, rally_id=rally_id)
        return obj

    def perform_update(self, serializer):
        # Guarda cambios y luego actualiza puntos
        serializer.save()
        equipo = serializer.instance
        equipo.actualizar_puntos()

class HistoricoPilotoView(generics.ListAPIView):
    serializer_class = ParticipacionPilotoSerializer

    def get_queryset(self):
        piloto_id = self.kwargs.get('piloto_id')
        return ParticipacionRally.objects.filter(piloto__id=piloto_id).order_by('-rally__id')


class HistoricoCopilotoView(generics.ListAPIView):
    serializer_class = ParticipacionCopilotoSerializer

    def get_queryset(self):
        copiloto_id = self.kwargs.get('copiloto_id')
        return ParticipacionRally.objects.filter(copiloto__id=copiloto_id).order_by('-rally__id')


class HistoricoCocheView(generics.ListAPIView):
    serializer_class = ParticipacionCocheSerializer

    def get_queryset(self):
        coche_id = self.kwargs.get('coche_id')
        return ParticipacionRally.objects.filter(coche__id=coche_id).order_by('-rally__id')