import logging
from apscheduler.schedulers.background import BackgroundScheduler

logger = logging.getLogger(__name__)
scheduler = BackgroundScheduler()
jobs_registrados = False

def start():
    global jobs_registrados

    if not scheduler.running:
        scheduler.start()
        logger.info("✅ Scheduler iniciado")
    else:
        logger.warning("⚠️ Scheduler ya estaba corriendo")

    if not jobs_registrados:
        registrar_jobs()
        jobs_registrados = True
    else:
        logger.warning("⚠️ Jobs ya registrados anteriormente")

def registrar_jobs():
    from .scheduler import clonar_equipos_del_dia, actualizar_puntos_rallies_finalizados

    scheduler.add_job(
        clonar_equipos_del_dia,
        'cron',
        hour=3,
        minute=11,
        id='clonacion_equipos_diaria',
        replace_existing=True
    )

    scheduler.add_job(
        actualizar_puntos_rallies_finalizados,
        'cron',
        hour=3,
        minute=23,
        id='actualizar_puntos_rallies',
        replace_existing=True
    )

    logger.info("✅ Jobs registrados correctamente en el scheduler")


def clonar_equipos_del_dia():
    from datetime import date
    from users.models import User
    from .models import Rally
    from .views import clonar_equipo_para_rally

    hoy = date(2025, 3, 21)  # ⚠️ cambiar por date.today() en producción
    logger.info(f"[Scheduler] Ejecutando clonación para: {hoy}")
    rallies = Rally.objects.filter(fecha_inicio=hoy)
    logger.info(f"[Scheduler] Rallies encontrados: {rallies.count()}")

    for rally in rallies:
        for user in User.objects.all():
            try:
                clonar_equipo_para_rally(user, rally)
            except Exception as e:
                logger.error(f"[Scheduler] Error clonando para {user}: {e}")


def actualizar_puntos_rallies_finalizados():
    from datetime import date, timedelta
    from .models import Rally, FantasyTeamRally

    hoy = date.today()
    fecha_limite = hoy - timedelta(days=3)
    rallies_a_actualizar = Rally.objects.filter(fecha_inicio__lte=fecha_limite)

    for rally in rallies_a_actualizar:
        equipos = FantasyTeamRally.objects.filter(rally=rally)
        for equipo in equipos:
            equipo.actualizar_puntos()
        logger.info(f"[Scheduler] Puntos actualizados para rally: {rally.nombre}")

    actualizar_puntos_de_ligas()
    logger.info("[Scheduler] Puntos de ligas actualizados")


def actualizar_puntos_de_ligas():
    from ligas.models import Liga
    from rally.models import FantasyTeamRally
    from django.db.models import Sum

    for liga in Liga.objects.all():
        for participacion in liga.participantes.all():
            puntos = FantasyTeamRally.objects.filter(
                user=participacion.usuario,
                rally__fecha_inicio__gte=participacion.fecha_union
            ).aggregate(Sum('puntos'))['puntos__sum'] or 0

            participacion.puntos = puntos
            participacion.save()
