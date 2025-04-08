from django.core.management.base import BaseCommand
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import re

from rally.models import Rally, Piloto, Copiloto, Coche, ParticipacionRally

class Command(BaseCommand):
    help = "Scrapea resultados de eWRC y los guarda en la base de datos"

    def handle(self, *args, **kwargs):
        driver = webdriver.Chrome()

        page_urls = [
            "https://www.ewrc-results.com/final/92248-rallye-tierras-altas-de-lorca-2025/",
            "https://www.ewrc-results.com/final/91078-rally-sierra-morena-cordoba-patrimonio-de-la-humanidad-2025/",
            "https://www.ewrc-results.com/final/92250-rally-de-ourense-recalvi-2025/",
            "https://www.ewrc-results.com/final/92251-rally-recalvi-rias-baixas-2025/",
            "https://www.ewrc-results.com/final/92253-rally-blendio-princesa-de-asturias-ciudad-de-oviedo-2025/",
            "https://www.ewrc-results.com/final/92275-rally-villa-de-llanes-2025/",
            "https://www.ewrc-results.com/final/92277-rallyracc-catalunya-costa-daurada-2025/",
            "https://www.ewrc-results.com/final/92278-rally-de-la-nucia-mediterraneo-costa-blanca-2025/",
        ]

        def format_name(full_name):
            parts = full_name.split()
            if len(parts) > 2 and parts[-2] in ["José", "Juan"]:
                first_name = f"{parts[-2]} {parts[-1]}"
                last_names = " ".join(parts[:-2])
            else:
                first_name = parts[-1]
                last_names = " ".join(parts[:-1])
            return f"{first_name} {last_names}" if last_names else first_name

        def extract_data_from_page():
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "h3.text-center.pt-2.pb-0"))
            )

            rally_name = driver.find_element(By.CSS_SELECTOR, "h3.text-center.pt-2.pb-0").text.strip()
            results_data = []

            try:
                rows = driver.find_elements(By.CSS_SELECTOR, "table.results tbody tr")
                for i in range(min(10, len(rows))):
                    try:
                        position = rows[i].find_element(By.CSS_SELECTOR, "td.font-weight-bold.text-left").text.strip()

                        flags = rows[i].find_elements(By.CSS_SELECTOR, "td.final-results-flag img")
                        driver_flag = flags[0].get_attribute("src") if len(flags) > 0 else None
                        co_driver_flag = flags[1].get_attribute("src") if len(flags) > 1 else None

                        entry_element = rows[i].find_element(By.CSS_SELECTOR, "td.final-entry a")
                        entry_text = entry_element.get_attribute("textContent").strip()
                        names = re.split(r'\s*-\s*', entry_text)

                        driver_name = format_name(names[0].strip()) if len(names) > 0 else ""
                        co_driver_name = format_name(names[1].strip()) if len(names) > 1 else ""

                        car_icon = rows[i].find_element(By.CSS_SELECTOR, "td.final-results-icon img").get_attribute("src")

                        car_info_raw = rows[i].find_element(By.CSS_SELECTOR, "td.final-results-car.font-weight-bold").text.strip()
                        car_info_lines = car_info_raw.split("\n")
                        car_info = car_info_lines[0] if car_info_lines else ""

                        team_name_elem = rows[i].find_elements(By.CSS_SELECTOR, "td.final-results-car.font-weight-bold .final-results-team")
                        team_name = team_name_elem[0].text.strip() if team_name_elem else ""

                        results_data.append({
                            "position": position,
                            "driver": driver_name,
                            "copilot": co_driver_name,
                            "driver_flag": driver_flag,
                            "co_driver_flag": co_driver_flag,
                            "car_icon": car_icon,
                            "car_info": car_info,
                            "team_name": team_name
                        })

                    except Exception as e:
                        print(f"Error en fila {i + 1}: {e}")
                        continue
            except Exception as e:
                print(f"Error general en tabla: {e}")

            return rally_name, results_data

        for url in page_urls:
            try:
                driver.get(url)
                rally_name, results_data = extract_data_from_page()

                rally_obj, _ = Rally.objects.get_or_create(nombre=rally_name)

                for entry in results_data:
                    piloto, _ = Piloto.objects.get_or_create(
                        nombre=entry["driver"],
                        defaults={"bandera": entry["driver_flag"], "precio": 100000.00}
                    )

                    copiloto, _ = Copiloto.objects.get_or_create(
                        nombre=entry["copilot"],
                        defaults={"bandera": entry["co_driver_flag"], "precio": 75000.00}
                    )

                    coche, _ = Coche.objects.get_or_create(
                        modelo=entry["car_info"],
                        defaults={"imagen": entry["car_icon"], "precio": 150000.00}
                    )

                    ParticipacionRally.objects.get_or_create(
                        rally=rally_obj,
                        piloto=piloto,
                        copiloto=copiloto,
                        coche=coche,
                        defaults={
                            "equipo": entry["team_name"],
                            "puntos": 0
                        }
                    )

                self.stdout.write(self.style.SUCCESS(f"Datos guardados de: {rally_name}"))
            except Exception as e:
                print(f"Error con la URL {url}: {e}")
                continue

        driver.quit()
