import re
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from django.core.management.base import BaseCommand
from rally.models import Rally


class Command(BaseCommand):
    help = "Scrapea la web y guarda los rallies 2025 en la base de datos"

    def extract_date_part(self, fecha_str, point_index):
        start_index = max(point_index - 2, 0)
        part = fecha_str[start_index:point_index].strip()
        if len(part) == 1:
            part = "0" + part
        return part

    def handle(self, *args, **options):
        driver = webdriver.Chrome()
        driver.get("https://www.ewrc-results.com/season/2025/?nat=8")

        WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".season-event"))
        )

        rally_containers = driver.find_elements(By.CSS_SELECTOR, ".season-event")

        for rally in rally_containers:
            try:
                rally_name = rally.find_element(By.CSS_SELECTOR, ".season-event-name a").text.strip()
                event_info = rally.find_element(By.CSS_SELECTOR, ".event-info").text.strip()
                fecha_raw = event_info.split(",")[0].strip()

                año = "2025"  # Año fijo asumido

                puntos = [i for i, c in enumerate(fecha_raw) if c == '.']

                if len(puntos) >= 3:
                    dia_inicio = self.extract_date_part(fecha_raw, puntos[0])
                    mes_inicio = self.extract_date_part(fecha_raw, puntos[1])
                    dia_fin = self.extract_date_part(fecha_raw, puntos[2])
                    mes_fin = (
                        self.extract_date_part(fecha_raw, puntos[3]) if len(puntos) > 3 else mes_inicio
                    )

                    fecha_inicio_str = f"{año}-{mes_inicio}-{dia_inicio}"
                    fecha_fin_str = f"{año}-{mes_fin}-{dia_fin}"

                    fecha_inicio = datetime.strptime(fecha_inicio_str, "%Y-%m-%d").date()
                    fecha_fin = datetime.strptime(fecha_fin_str, "%Y-%m-%d").date()
                else:
                    self.stdout.write(self.style.WARNING(f"Fecha no válida para {rally_name}"))
                    fecha_inicio = None
                    fecha_fin = None

                rally_obj, created = Rally.objects.update_or_create(
                    nombre=rally_name,
                    defaults={
                        "fecha_inicio": fecha_inicio,
                        "fecha_fin": fecha_fin,
                    },
                )

                if created:
                    self.stdout.write(self.style.SUCCESS(f"Rally creado: {rally_name}"))
                else:
                    self.stdout.write(self.style.SUCCESS(f"Rally actualizado: {rally_name}"))

            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Error al procesar rally: {e}"))
                continue

        driver.quit()
