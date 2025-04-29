import json
import re
from django.core.management.base import BaseCommand
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from rally.models import Rally, Piloto, Copiloto, Coche, ParticipacionRally

class Command(BaseCommand):
    help = 'Scrapea los resultados de eWRC y los guarda en la base de datos'

    def handle(self, *args, **kwargs):
        # Inicializar el driver
        driver = webdriver.Chrome()

        # URLs de las páginas que deseas recorrer
        page_urls = [
            "https://www.ewrc-results.com/entries/92248-rallye-tierras-altas-de-lorca-2025/?sct=1512",
            "https://www.ewrc-results.com/entries/91078-rally-sierra-morena-cordoba-patrimonio-de-la-humanidad-2025/?sct=1512",
            # Puedes agregar más URLs aquí
        ]

        # Lista para almacenar los datos
        rallies_data = []

        # Función para formatear el nombre correctamente
        def format_name(full_name):
            parts = full_name.split()

            # Eliminar "jnr", "jr", "jr." si están al final
            if parts[-1].lower().rstrip(".") in ["jnr", "jr"]:
                parts = parts[:-1]

            # Lista de nombres compuestos comunes
            composed_names = [
                "José Luis", "Juan Carlos", "María José", "Luis Miguel", "Ana María",
                "José Manuel", "Juan José", "Juan Manuel", "Miguel Ángel",
                "José Antonio", "María del Mar", "José María"
            ]

            # Detectar nombre compuesto de las dos últimas palabras
            if len(parts) >= 2:
                last_two = f"{parts[-2]} {parts[-1]}"
                if last_two in composed_names:
                    first_name = last_two
                    last_names = " ".join(parts[:-2])
                    return f"{first_name} {last_names}" if last_names else first_name

            # Lógica general por defecto
            first_name = parts[-1]
            last_names = " ".join(parts[:-1])
            return f"{first_name} {last_names}" if last_names else first_name

        # Función para extraer los datos
        def extract_data_from_page():
            WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.CSS_SELECTOR, "table.results")))

            try:
                rally_name = driver.find_element(By.CSS_SELECTOR, "h3.text-center.pt-2.pb-0").text.strip()
            except Exception as e:
                print(f"Error al obtener el nombre del rally: {e}")
                return None, []

            results_data = []

            try:
                rows = driver.find_elements(By.CSS_SELECTOR, "table.results tbody tr")
                if not rows:
                    print(f"No se encontraron filas de resultados en la página: {rally_name}.")
                    return rally_name, results_data

                for i in range(len(rows)):  # Recorrer todas las filas
                    try:
                        dorsal = rows[i].find_element(By.CSS_SELECTOR, "td.text-left.font-weight-bold.text-primary").text.strip()

                        startlist_entry = rows[i].find_element(By.CSS_SELECTOR, "td.startlist-entry")
                        driver_name_elem = startlist_entry.find_element(By.CSS_SELECTOR, "div.startlist-driver a")
                        driver_name = format_name(driver_name_elem.text.strip())

                        co_driver_name_elem = startlist_entry.find_elements(By.CSS_SELECTOR, "div.startlist-driver a")[1] if len(startlist_entry.find_elements(By.CSS_SELECTOR, "div.startlist-driver a")) > 1 else None
                        co_driver_name = format_name(co_driver_name_elem.text.strip()) if co_driver_name_elem else ""

                        driver_flag = startlist_entry.find_element(By.CSS_SELECTOR, "div.startlist-driver img").get_attribute("src")
                        co_driver_flag = startlist_entry.find_elements(By.CSS_SELECTOR, "div.startlist-driver img")[1].get_attribute("src") if len(startlist_entry.find_elements(By.CSS_SELECTOR, "div.startlist-driver img")) > 1 else ""

                        car_icon = rows[i].find_element(By.CSS_SELECTOR, "td.startlist-icon img").get_attribute("src")
                        car_info = rows[i].find_element(By.CSS_SELECTOR, "td.font-weight-bold.lh-130").text.strip().split("\n")[0]

                        if any(keyword in car_info for keyword in ["Rally2", "R5", "Rally4", "N5", "RZ", "Rally3"]):
                            try:
                                team_name_elem = rows[i].find_element(By.CSS_SELECTOR, "td.font-weight-bold.lh-130 span")
                                team_name = team_name_elem.text.strip()
                            except Exception:
                                team_name = "Sin equipo"

                            results_data.append({
                                "dorsal": dorsal,
                                "driver": driver_name,
                                "copilot": co_driver_name,
                                "driver_flag": driver_flag,
                                "co_driver_flag": co_driver_flag,
                                "car_icon": car_icon,
                                "car_info": car_info,
                                "team_name": team_name
                            })

                    except Exception as e:
                        print(f"Error al procesar la fila {i + 1} en {rally_name}: {e}")
                        continue
            except Exception as e:
                print(f"Error al capturar los resultados en {rally_name}: {e}")

            return rally_name, results_data

        # Recorrer todos los enlaces
        for url in page_urls:
            try:
                driver.get(url)
                rally_name, results_data = extract_data_from_page()

                if results_data:
                    # Guardamos los datos en la base de datos
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

                        # Participación en el rally
                        ParticipacionRally.objects.get_or_create(
                            rally=rally_obj,
                            piloto=piloto,
                            copiloto=copiloto,
                            coche=coche,
                            defaults={"equipo": entry["team_name"], "puntos": 0}
                        )

                    self.stdout.write(self.style.SUCCESS(f"Datos extraídos y guardados para el rally: {rally_name}"))
                else:
                    self.stdout.write(self.style.WARNING(f"No se encontraron resultados en la página: {url}. Deteniendo el proceso."))
                    driver.quit()
                    break  # Detenemos el proceso si no hay datos en alguna página.

            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Error al procesar la página {url}. Detalles del error: {e}"))
                continue

        # Cerrar el driver después de procesar todos los resultados
        driver.quit()
