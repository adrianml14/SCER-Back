# rally/management/commands/actualizar_puntos.py
from django.core.management.base import BaseCommand
from rally.scheduler import actualizar_puntos_rally_y_ligas
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Actualiza puntos de rally y ligas (puede ejecutarse manualmente o desde scheduler)'

    def handle(self, *args, **options):
        logger.info("Ejecutando actualización manual de puntos...")
        actualizar_puntos_rally_y_ligas()
        logger.info("Actualización manual de puntos finalizada.")
        self.stdout.write(self.style.SUCCESS('Puntos actualizados correctamente.'))
