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
    from .scheduler import programar_scrappers_y_jobs_por_rally
    programar_scrappers_y_jobs_por_rally()
    logger.info("✅ Jobs programados por rally correctamente")

def programar_scrappers_y_jobs_por_rally():
    from rally.models import Rally
    from django.core.management import call_command
    from datetime import datetime, timedelta

    rallies = Rally.objects.filter(fecha_inicio__isnull=False)

    for rally in rallies:
        nombre = rally.nombre
        fecha_inicio = rally.fecha_inicio

        # 1. Clonar equipos el mismo día del rally a las 03:00
        fecha_clonacion = datetime.combine(fecha_inicio, datetime.min.time()) + timedelta(hours=3)
        scheduler.add_job(
            clonar_equipos_del_dia,
            'date',
            run_date=fecha_clonacion,
            id=f'clonar_equipos_{rally.id}',
            replace_existing=True
        )
        logger.info(f"🗓️ Clonación de equipos programada para rally '{nombre}' el {fecha_clonacion}")

        # 2. Scraping de inscritos 2 día antes
        fecha_inscritos = datetime.combine(fecha_inicio - timedelta(days=2), datetime.min.time()) + timedelta(hours=9, minutes=58)
        scheduler.add_job(
            lambda: call_command('webscrappingINSCRITOS'),
            'date',
            run_date=fecha_inscritos,
            id=f'webscrapping_inscritos_{rally.id}',
            replace_existing=True
        )
        logger.info(f"🗓️ webscrappingINSCRITOS programado para rally '{nombre}' el {fecha_inscritos}")

        # 3. Scraping de resultados 3 días después del inicio del rally
        fecha_resultados = datetime.combine(fecha_inicio + timedelta(days=2), datetime.min.time()) + timedelta(hours=9, minutes=12)
        scheduler.add_job(
            lambda: call_command('webscrappingRESULTADOS'),
            'date',
            run_date=fecha_resultados,
            id=f'webscrapping_resultados_{rally.id}',
            replace_existing=True
        )
        logger.info(f"🗓️ webscrappingRESULTADOS programado para rally '{nombre}' el {fecha_resultados}")

        # 4. Actualizar puntos justo después (05:10)
        fecha_puntos = fecha_resultados + timedelta(minutes=1)
        scheduler.add_job(
            actualizar_puntos_rally_y_ligas,
            'date',
            run_date=fecha_puntos,
            id=f'actualizar_puntos_{rally.id}',
            replace_existing=True
        )
        logger.info(f"🗓️ Actualización de puntos programada para rally '{nombre}' el {fecha_puntos}")

def clonar_equipos_del_dia():
    from datetime import date
    from users.models import User
    from .models import Rally
    from .views import clonar_equipo_para_rally

    hoy = date.today()
    logger.info(f"[Scheduler] Ejecutando clonación para: {hoy}")
    rallies = Rally.objects.filter(fecha_inicio=hoy)
    logger.info(f"[Scheduler] Rallies encontrados: {rallies.count()}")

    for rally in rallies:
        for user in User.objects.all():
            try:
                clonar_equipo_para_rally(user, rally)
            except Exception as e:
                logger.error(f"[Scheduler] Error clonando para {user}: {e}")

def actualizar_puntos_rally_y_ligas():
    from datetime import date, timedelta
    from .models import Rally, FantasyTeamRally
    from ligas.models import Liga
    from django.db.models import Sum

    hoy = date.today()
    fecha_limite = hoy - timedelta(days=3)
    rallies_a_actualizar = Rally.objects.filter(fecha_inicio__lte=fecha_limite)

    for rally in rallies_a_actualizar:
        equipos = FantasyTeamRally.objects.filter(rally=rally)
        for equipo in equipos:
            equipo.actualizar_puntos()
        logger.info(f"[Scheduler] Puntos actualizados para rally: {rally.nombre}")

    logger.info("[Scheduler] Actualizando puntos de ligas")
    for liga in Liga.objects.all():
        for participacion in liga.participantes.all():
            puntos = FantasyTeamRally.objects.filter(
                user=participacion.usuario,
                rally__fecha_inicio__gte=participacion.fecha_union
            ).aggregate(Sum('puntos'))['puntos__sum'] or 0

            participacion.puntos = int(puntos)
            participacion.save()
