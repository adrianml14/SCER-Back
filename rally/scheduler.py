
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import date, timedelta
from users.models import User
from .models import FantasyTeamRally, Rally
from .views import clonar_equipo_para_rally
from ligas.models import ParticipacionLiga
from rally.models import FantasyTeamRally
from django.db.models import Sum


def start():
    scheduler = BackgroundScheduler()

    scheduler.add_job(
        clonar_equipos_del_dia,
        'cron',
        hour=13,
        minute=6,
        id='clonacion_equipos_diaria',
        replace_existing=True
    )

    scheduler.add_job(
        actualizar_puntos_rallies_finalizados,
        'cron',
        hour=13,
        minute=56,
        id='actualizar_puntos_rallies',
        replace_existing=True
    )

    scheduler.start()

def clonar_equipos_del_dia():
    # Para prueba, pon fecha fija que sí exista en DB
    hoy = date(2025, 3, 21)
    print(f"[Scheduler] Ejecutando para fecha: {hoy}")
    rallies = Rally.objects.filter(fecha_inicio=hoy)
    print(f"[Scheduler] Rallies encontrados: {rallies.count()}")
    for rally in rallies:
        print(f"[Scheduler] Procesando rally: {rally}")
        for user in User.objects.all():
            print(f"[Scheduler] Clonando equipo para usuario: {user}")
            try:
                clonar_equipo_para_rally(user, rally)
            except Exception as e:
                print(f"[Scheduler] Error clonando equipo para {user}: {e}")


def actualizar_puntos_rallies_finalizados():
    hoy = date.today()
    fecha_limite = hoy - timedelta(days=3)
    rallies_a_actualizar = Rally.objects.filter(fecha_inicio__lte=fecha_limite)

    for rally in rallies_a_actualizar:
        equipos = FantasyTeamRally.objects.filter(rally=rally)
        for equipo in equipos:
            equipo.actualizar_puntos()
        print(f"[Scheduler] Puntos actualizados para rally: {rally.nombre}")

    actualizar_puntos_de_ligas()
    print("[Scheduler] Puntos de ligas actualizados.")


def actualizar_puntos_de_ligas():
    from ligas.models import Liga  # evitar import circular

    for liga in Liga.objects.all():
        for participacion in liga.participantes.all():
            puntos = FantasyTeamRally.objects.filter(
                user = participacion.usuario,
                rally__fecha_inicio__gte=participacion.fecha_union
            ).aggregate(Sum('puntos'))['puntos__sum'] or 0

            participacion.puntos = puntos
            participacion.save()
