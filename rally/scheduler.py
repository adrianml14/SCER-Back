# rally/scheduler.py
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import date
from users.models import User
from .models import Rally
from .views import clonar_equipo_para_rally

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
    scheduler.start()
