import os
import django
import re
from django.core.management.base import BaseCommand
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from rally.models import Piloto, Copiloto, Coche, Rally, ParticipacionRally

class Command(BaseCommand):
    help = 'Scrapea resultados de rally y los guarda en la base de datos'

    def handle(self, *args, **kwargs):
        # Inicializar Selenium
        driver = webdriver.Chrome()

        # URLs a recorrer
        page_urls = [
            "https://www.ewrc-results.com/final/92248-rallye-tierras-altas-de-lorca-2025/?sct=1512",
            "https://www.ewrc-results.com/final/91078-rally-sierra-morena-cordoba-patrimonio-de-la-humanidad-2025/?sct=1512",
            "https://www.ewrc-results.com/final/92250-rally-de-ourense-recalvi-2025/?sct=1512",
            "https://www.ewrc-results.com/final/92251-rally-recalvi-rias-baixas-2025/?sct=1512",
            "https://www.ewrc-results.com/final/92253-rally-blendio-princesa-de-asturias-ciudad-de-oviedo-2025/?sct=1512",
            "https://www.ewrc-results.com/final/92275-rally-villa-de-llanes-2025/?sct=1512",
            "https://www.ewrc-results.com/final/92277-rallyracc-catalunya-costa-daurada-2025/?sct=1512",
            "https://www.ewrc-results.com/final/92278-rally-de-la-nucia-mediterraneo-costa-blanca-2025/?sct=1512",
        ]

        def format_name(full_name):
            parts = full_name.split()

            if parts and parts[-1].lower().rstrip(".") in ["jnr", "jr"]:
                parts = parts[:-1]

            composed_names = [
                "José Luis", "Juan Carlos", "María José", "Luis Miguel", "Ana María",
                "José Manuel", "Juan José", "Juan Manuel", "Miguel Ángel",
                "José Antonio", "María del Mar", "José María"
            ]

            if len(parts) >= 2:
                last_two = f"{parts[-2]} {parts[-1]}"
                if last_two in composed_names:
                    first_name = last_two
                    last_names = " ".join(parts[:-2])
                    return f"{first_name} {last_names}" if last_names else first_name

            if parts:
                first_name = parts[-1]
                last_names = " ".join(parts[:-1])
                return f"{first_name} {last_names}" if last_names else first_name

            return full_name


        def extract_data():
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "h3.text-center.pt-2.pb-0"))
            )

            rally_name = driver.find_element(By.CSS_SELECTOR, "h3.text-center.pt-2.pb-0").text.strip()

            # Buscar rally con nombre igual (ignorando mayúsculas)
            rally_obj = Rally.objects.filter(nombre__iexact=rally_name).first()
            if not rally_obj:
                rally_obj = Rally.objects.create(nombre=rally_name)

            try:
                rows = driver.find_elements(By.CSS_SELECTOR, "table.results tbody tr")
                if not rows:
                    self.stdout.write(self.style.WARNING(f"No hay resultados para: {rally_name}"))
                    return False

                for i in range(min(10, len(rows))):
                    try:
                        pos = rows[i].find_element(By.CSS_SELECTOR, "td.font-weight-bold.text-left").text.strip()

                        # Extraer sólo los dígitos para la posición
                        match = re.search(r'\d+', pos)
                        posicion_int = int(match.group()) if match else None

                        flags = rows[i].find_elements(By.CSS_SELECTOR, "td.final-results-flag img")
                        driver_flag = flags[0].get_attribute("src") if len(flags) > 0 else ""
                        copilot_flag = flags[1].get_attribute("src") if len(flags) > 1 else ""

                        names_raw = rows[i].find_element(By.CSS_SELECTOR, "td.final-entry a").text.strip()
                        names = re.split(r'\s*-\s*', names_raw)
                        driver_name = format_name(names[0]) if len(names) > 0 else ""
                        copilot_name = format_name(names[1]) if len(names) > 1 else ""

                        car_icon = rows[i].find_element(By.CSS_SELECTOR, "td.final-results-icon img").get_attribute("src")
                        car_info = rows[i].find_element(By.CSS_SELECTOR, "td.final-results-car.font-weight-bold").text.strip().split("\n")[0]

                        team_elems = rows[i].find_elements(By.CSS_SELECTOR, ".final-results-team")
                        team_name = team_elems[0].text.strip() if team_elems else ""

                        piloto_obj, _ = Piloto.objects.get_or_create(nombre=driver_name, defaults={"bandera": driver_flag})
                        copiloto_obj, _ = Copiloto.objects.get_or_create(nombre=copilot_name, defaults={"bandera": copilot_flag})
                        coche_obj, _ = Coche.objects.get_or_create(modelo=car_info, defaults={"imagen": car_icon})

                        participacion, _ = ParticipacionRally.objects.get_or_create(
                            rally=rally_obj,
                            piloto=piloto_obj,
                            copiloto=copiloto_obj,
                            coche=coche_obj,
                            defaults={"equipo": team_name, "dorsal": ""}
                        )
                        participacion.posicion = posicion_int
                        participacion.equipo = team_name
                        participacion.puntos = 0

                        participacion.save()
                    except Exception as e:
                        self.stdout.write(self.style.ERROR(f"Error en fila {i + 1}: {e}"))
                        continue
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Error extrayendo resultados de {rally_name}: {e}"))
                return False

            self.stdout.write(self.style.SUCCESS(f"✔️ Datos insertados para {rally_name}"))
            return True

        for url in page_urls:
            try:
                driver.get(url)
                result = extract_data()
                if not result:
                    self.stdout.write(self.style.WARNING("🚫 Página vacía, deteniendo scraping."))
                    break
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"⚠️ Error procesando {url}: {e}"))
                continue

        driver.quit()
