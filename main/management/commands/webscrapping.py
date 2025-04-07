import re
import sys
from django.core.management.base import BaseCommand
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from users.models import User
from rally.models import Rally, Piloto, Copiloto, Coche, Participante

# -- CONFIGURACIÓN --
RALLY_URLS = [
    "https://www.ewrc-results.com/entries/92248-rallye-tierras-altas-de-lorca-2025/?sct=1512",
    "https://www.ewrc-results.com/entries/91078-rally-sierra-morena-cordoba-patrimonio-de-la-humanidad-2025/?sct=1512",
    # Agrega más si quieres
]

def format_name(full_name):
    parts = full_name.split()
    if parts[-1].lower().rstrip(".") in ["jnr", "jr"]:
        parts = parts[:-1]
    first_name = parts[-1]
    last_names = " ".join(parts[:-1])
    return f"{first_name} {last_names}" if last_names else first_name

class Command(BaseCommand):
    help = "Scrapea los rallies y guarda datos en la base de datos"

    def handle(self, *args, **kwargs):
        driver = webdriver.Chrome()

        for url in RALLY_URLS:
            try:
                driver.get(url)
                WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.CSS_SELECTOR, "table.results")))

                rally_name = driver.find_element(By.CSS_SELECTOR, "h3.text-center.pt-2.pb-0").text.strip()
                rally_obj, _ = Rally.objects.get_or_create(nombre=rally_name)

                # 🧹 Eliminar inscripciones anteriores del rally
                rally_obj.participantes.all().delete()

                rows = driver.find_elements(By.CSS_SELECTOR, "table.results tbody tr")
                for row in rows:
                    try:
                        dorsal = row.find_element(By.CSS_SELECTOR, "td.text-left.font-weight-bold.text-primary").text.strip()

                        startlist_entry = row.find_element(By.CSS_SELECTOR, "td.startlist-entry")
                        driver_name_elem = startlist_entry.find_element(By.CSS_SELECTOR, "div.startlist-driver a")
                        driver_name = format_name(driver_name_elem.text.strip())
                        co_driver_name_elem = startlist_entry.find_elements(By.CSS_SELECTOR, "div.startlist-driver a")[1]
                        co_driver_name = format_name(co_driver_name_elem.text.strip()) if co_driver_name_elem else None

                        driver_flag = startlist_entry.find_element(By.CSS_SELECTOR, "div.startlist-driver img").get_attribute("src")
                        co_driver_flag = startlist_entry.find_elements(By.CSS_SELECTOR, "div.startlist-driver img")[1].get_attribute("src") if co_driver_name else None

                        car_icon = row.find_element(By.CSS_SELECTOR, "td.startlist-icon img").get_attribute("src")
                        car_info = row.find_element(By.CSS_SELECTOR, "td.font-weight-bold.lh-130").text.strip().split("\n")[0]
                        clase = next((c for c in ["Rally2", "R5", "Rally4", "N5"] if c in car_info), "Otros")

                        try:
                            team_name = row.find_element(By.CSS_SELECTOR, "td.font-weight-bold.lh-130 span").text.strip()
                        except:
                            team_name = ""

                        # 🔄 Usuarios (Piloto y Copiloto)
                        piloto_user, _ = User.objects.get_or_create(email=f"{driver_name.lower().replace(' ', '_')}@piloto.com", defaults={"name": driver_name, "password": "default"})
                        copiloto_user = None
                        if co_driver_name:
                            copiloto_user, _ = User.objects.get_or_create(email=f"{co_driver_name.lower().replace(' ', '_')}@copiloto.com", defaults={"name": co_driver_name, "password": "default"})

                        # 🏁 Piloto / Copiloto
                        piloto, _ = Piloto.objects.get_or_create(usuario=piloto_user, defaults={"bandera": driver_flag})
                        copiloto = None
                        if copiloto_user:
                            copiloto, _ = Copiloto.objects.get_or_create(usuario=copiloto_user, defaults={"bandera": co_driver_flag})

                        # 🚗 Coche
                        coche, _ = Coche.objects.get_or_create(marca_modelo=car_info, defaults={"clase": clase, "icono_url": car_icon})

                        # ➕ Participante
                        Participante.objects.create(
                            rally=rally_obj,
                            dorsal=dorsal,
                            piloto=piloto,
                            copiloto=copiloto,
                            coche=coche,
                            equipo=team_name
                        )

                    except Exception as row_error:
                        print(f"[!] Error procesando fila: {row_error}")

                print(f"[✓] Procesado {rally_name}")

            except Exception as e:
                print(f"[!] Error procesando {url}: {e}")
                continue

        driver.quit()
        print("✔ Webscrapping terminado correctamente.")
