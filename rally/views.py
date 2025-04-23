from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Piloto, Copiloto, Coche, FantasyTeam
from .serializer import PilotoSerializer, CopilotoSerializer, CocheSerializer
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