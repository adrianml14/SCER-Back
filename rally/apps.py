import os
from django.apps import AppConfig
from rally import scheduler


class RallyConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'rally'

    def ready(self):
        # Importa e inicia el scheduler aquí
        if os.environ.get('RUN_MAIN') == 'true':
            from rally import scheduler
            scheduler.start()
