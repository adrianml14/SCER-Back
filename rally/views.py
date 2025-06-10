from datetime import date
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Sum

from users.models import User
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
                if equipo.pilotos.count() >= 2:
                    return Response({'error': 'No puedes tener más de 2 pilotos.'}, status=status.HTTP_400_BAD_REQUEST)
            elif tipo == 'copiloto':
                elemento = Copiloto.objects.get(id=id_elemento)
                if equipo.copilotos.count() >= 2:
                    return Response({'error': 'No puedes tener más de 2 copilotos.'}, status=status.HTTP_400_BAD_REQUEST)
            elif tipo == 'coche':
                elemento = Coche.objects.get(id=id_elemento)
                if equipo.coches.count() >= 1:
                    return Response({'error': 'Solo puedes tener 1 coche en tu equipo.'}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({'error': 'Tipo de elemento no válido.'}, status=status.HTTP_400_BAD_REQUEST)

            if equipo.presupuesto < elemento.precio:
                return Response({'error': 'No tienes suficiente presupuesto.'}, status=status.HTTP_400_BAD_REQUEST)

            # Agregar elemento y descontar presupuesto
            if tipo == 'piloto':
                equipo.pilotos.add(elemento)
            elif tipo == 'copiloto':
                equipo.copilotos.add(elemento)
            elif tipo == 'coche':
                equipo.coches.add(elemento)

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
            # Filtramos usuarios que se registraron antes o el mismo día que empezó el rally
            participaciones = FantasyTeamRally.objects.filter(
                rally=rally,
                user__fecha_registro__lte=rally.fecha_inicio
            ).select_related('user').order_by('-puntos')

            items = []
            for p in participaciones:
                try:
                    equipo_nombre = FantasyTeam.objects.get(user=p.user).nombre
                except FantasyTeam.DoesNotExist:
                    equipo_nombre = "Equipo desconocido"

                items.append({
                    'usuario': p.user.username,
                    'puntos': p.puntos,
                    'equipo_nombre': equipo_nombre,
                    'rally': rally.nombre
                })

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


def clonar_equipo_para_rally(user, rally):
    try:
        equipo = FantasyTeam.objects.get(user=user)

        # Solo copiar si la última modificación fue antes del inicio del rally
        if equipo.ultima_modificacion.date() <= rally.fecha_inicio:
            equipo_rally, created = FantasyTeamRally.objects.get_or_create(user=user, rally=rally)

            # Solo clonar si se acaba de crear (no sobrescribir si ya existe)
            if created:
                equipo_rally.pilotos.set(equipo.pilotos.all())
                equipo_rally.copilotos.set(equipo.copilotos.all())
                equipo_rally.coches.set(equipo.coches.all())
                equipo_rally.save()
                print(f"[Scheduler] Equipo de {user.email} clonado para el rally '{rally.nombre}'")
                print(f"  Pilotos: {[p.nombre for p in equipo_rally.pilotos.all()]}")
                print(f"  Copilotos: {[c.nombre for c in equipo_rally.copilotos.all()]}")
                print(f"  Coches: {[co.modelo for co in equipo_rally.coches.all()]}")
            else:
                print(f"[Scheduler] Equipo para {user.email} y rally '{rally.nombre}' ya existe, no se clonó")
        else:
            print(f"[Scheduler] Equipo para {user.email} modificado después del inicio del rally, no se clona")
    except FantasyTeam.DoesNotExist:
        print(f"[Scheduler] No existe equipo para el usuario {user.email}")


class ClasificacionGeneralView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        clasificacion = (
            FantasyTeamRally.objects
            .values('user__username')
            .annotate(puntos_totales=Sum('puntos'))
            .order_by('-puntos_totales')
        )

        data = []
        for idx, item in enumerate(clasificacion, start=1):
            try:
                equipo = FantasyTeam.objects.get(user__username=item['user__username'])
                nombre_equipo = equipo.nombre
            except FantasyTeam.DoesNotExist:
                nombre_equipo = "Equipo desconocido"

            data.append({
                'posicion': idx,
                'usuario': item['user__username'],
                'equipo_nombre': nombre_equipo,
                'puntos_totales': item['puntos_totales']
            })

        return Response(data)


hoy = date.today()
rallies = Rally.objects.filter(fecha_inicio=hoy)

for rally in rallies:
    for user in User.objects.all():
        clonar_equipo_para_rally(user, rally)