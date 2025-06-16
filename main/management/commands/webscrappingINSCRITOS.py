from decimal import Decimal
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
        # Inicializa el navegador Chrome
        driver = webdriver.Chrome()

        # Lista de URLs a scrapear (cada una representa una prueba de rally)
        page_urls = [
            # Ejemplo de rallies de la temporada 2025
            "https://www.ewrc-results.com/entries/92248-rallye-tierras-altas-de-lorca-2025/?sct=1512",
            # ...
        ]

        # Función auxiliar para formatear correctamente nombres (por ejemplo: José Luis Pérez)
        def format_name(full_name):
            parts = full_name.split()

            # Elimina sufijos como 'jr', 'jnr', etc.
            if parts[-1].lower().rstrip(".") in ["jnr", "jr"]:
                parts = parts[:-1]

            # Lista de nombres compuestos comunes
            composed_names = [
                "José Luis", "Juan Carlos", "María José", "Luis Miguel", "Ana María",
                "José Manuel", "Juan José", "Juan Manuel", "Miguel Ángel",
                "José Antonio", "María del Mar", "José María"
            ]

            # Verifica si las dos últimas palabras forman un nombre compuesto
            if len(parts) >= 2:
                last_two = f"{parts[-2]} {parts[-1]}"
                if last_two in composed_names:
                    first_name = last_two
                    last_names = " ".join(parts[:-2])
                    return f"{first_name} {last_names}" if last_names else first_name

            # Si no es compuesto, separa nombre y apellidos
            first_name = parts[-1]
            last_names = " ".join(parts[:-1])
            return f"{first_name} {last_names}" if last_names else first_name

        # Función que extrae datos de la página actual del navegador
        def extract_data_from_page():
            # Espera hasta que la tabla de resultados esté presente
            WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.CSS_SELECTOR, "table.results")))

            try:
                # Obtiene el nombre del rally
                rally_name = driver.find_element(By.CSS_SELECTOR, "h3.text-center.pt-2.pb-0").text.strip()
            except Exception as e:
                print(f"Error al obtener el nombre del rally: {e}")
                return None, []

            results_data = []

            try:
                # Encuentra todas las filas de resultados
                rows = driver.find_elements(By.CSS_SELECTOR, "table.results tbody tr")
                if not rows:
                    print(f"No se encontraron filas de resultados en la página: {rally_name}.")
                    return rally_name, results_data

                # Recorre cada fila de resultados
                for i in range(len(rows)):
                    try:
                        # Obtiene el número dorsal
                        dorsal = rows[i].find_element(By.CSS_SELECTOR, "td.text-left.font-weight-bold.text-primary").text.strip()

                        # Sección donde están piloto y copiloto
                        startlist_entry = rows[i].find_element(By.CSS_SELECTOR, "td.startlist-entry")
                        driver_name_elem = startlist_entry.find_element(By.CSS_SELECTOR, "div.startlist-driver a")
                        driver_name = format_name(driver_name_elem.text.strip())

                        # Copiloto (puede que no exista)
                        co_driver_name_elem = startlist_entry.find_elements(By.CSS_SELECTOR, "div.startlist-driver a")[1] if len(startlist_entry.find_elements(By.CSS_SELECTOR, "div.startlist-driver a")) > 1 else None
                        co_driver_name = format_name(co_driver_name_elem.text.strip()) if co_driver_name_elem else ""

                        # Banderas (icono del país)
                        driver_flag = startlist_entry.find_element(By.CSS_SELECTOR, "div.startlist-driver img").get_attribute("src")
                        co_driver_flag = startlist_entry.find_elements(By.CSS_SELECTOR, "div.startlist-driver img")[1].get_attribute("src") if len(startlist_entry.find_elements(By.CSS_SELECTOR, "div.startlist-driver img")) > 1 else ""

                        # Icono del coche y nombre del modelo
                        car_icon = rows[i].find_element(By.CSS_SELECTOR, "td.startlist-icon img").get_attribute("src")
                        car_info = rows[i].find_element(By.CSS_SELECTOR, "td.font-weight-bold.lh-130").text.strip().split("\n")[0]

                        # Solo guardar coches de ciertas categorías (filtrado)
                        if any(keyword in car_info for keyword in ["Rally2", "R5", "Rally4", "N5", "RZ", "Rally3"]):
                            try:
                                # Nombre del equipo (si está presente)
                                team_name_elem = rows[i].find_element(By.CSS_SELECTOR, "td.font-weight-bold.lh-130 span")
                                team_name = team_name_elem.text.strip()
                            except Exception:
                                team_name = "Sin equipo"

                            # Guarda los datos en la lista de resultados
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

        # Procesar cada URL de rally
        for url in page_urls:
            try:
                driver.get(url)  # Navegar a la URL
                rally_name, results_data = extract_data_from_page()  # Extraer los datos

                if not rally_name:
                    self.stdout.write(self.style.WARNING(f"No se pudo obtener el nombre del rally en la página: {url}"))
                    continue

                if results_data:
                    # Buscar el rally existente en la base de datos
                    try:
                        rally_obj = Rally.objects.get(nombre=rally_name)
                    except Rally.DoesNotExist:
                        self.stdout.write(self.style.WARNING(
                            f"El rally '{rally_name}' no está en la base de datos. Se omite esta página."
                        ))
                        continue  # Saltar si no existe

                    # Registrar los datos extraídos en la base de datos
                    for entry in results_data:
                        # Obtener o crear el piloto
                        piloto, _ = Piloto.objects.get_or_create(
                            nombre=entry["driver"],
                            defaults={"bandera": entry["driver_flag"], "precio": Decimal("100000.00")}
                        )

                        # Obtener o crear el copiloto
                        copiloto, _ = Copiloto.objects.get_or_create(
                            nombre=entry["copilot"],
                            defaults={"bandera": entry["co_driver_flag"], "precio": Decimal("100000.00")}
                        )

                        # Obtener o crear el coche
                        coche, _ = Coche.objects.get_or_create(
                            modelo=entry["car_info"],
                            defaults={"imagen": entry["car_icon"], "precio":Decimal("75000.00")}
                        )

                        # Registrar la participación en el rally
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
                    break  # Se detiene si una página no tiene datos válidos

            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Error al procesar la página {url}. Detalles del error: {e}"))
                continue

        # Cierra el navegador al final
        driver.quit()
