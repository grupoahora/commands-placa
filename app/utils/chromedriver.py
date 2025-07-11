from selenium import webdriver
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options  # ⚠️ CAMBIA Chrome -> Edge
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import time
import os
from datetime import datetime


def get_driver(placa, idplacahistory, path):
    options = uc.ChromeOptions()

    options.use_chromium = True  # Necesario para que se comporte como Chrome


    # Configuración headless + descarga
    options = Options()
    options.add_argument("--headless=new")  # usa el nuevo modo headless
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-background-networking")
    options.add_argument("--disable-sync")
    options.add_argument("--disable-default-apps")
    options.add_argument("--disable-popup-blocking")
    options.add_argument("--disable-translate")
    options.add_argument("--metrics-recording-only")
    options.add_argument("--mute-audio")
    options.add_argument("--no-first-run")
    options.add_argument("--safebrowsing-disable-auto-update")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--window-size=1920,1080")

    options.add_experimental_option("prefs", {
        "download.default_directory": path,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True,
        "plugins.always_open_pdf_externally": True  # 🔥 Importante para que Edge descargue PDF
    })

    driver = uc.Chrome(
        options=options,
        use_subprocess=True)
    return driver

    
    
def find_element_by(driver, method, value, timeout=10):
    """Busca un elemento usando el método y valor especificado.
    Retorna el elemento si se encuentra, o None si no."""
    try:
        WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((method, value))
        )
        return driver.find_element(method, value)
    except TimeoutException:
        return None
def wait_attr_by_find_element(driver, element, attr, timeout=10):
    """Espera a que un atributo de un elemento esté presente."""
    WebDriverWait(driver, timeout).until(
        lambda d: element.get_attribute(attr) != ""
    )
def wait_for_page_load(driver, url):
    """Espera a que la página cambie de URL después del inicio de sesión."""
    WebDriverWait(driver, 10).until(EC.url_changes(url))

def wait_for_page_load_complete(driver):
    """Espera a que la página cargue completamente."""
    WebDriverWait(driver, 10).until(
        lambda d: d.execute_script("return document.readyState") == "complete"
    )

def take_screenshot(driver, path="captura.png"):
    """Toma una captura de pantalla y la guarda en la ruta especificada."""
    time.sleep(5)  # Breve pausa para asegurarse de que la página haya cargado completamente
    driver.save_screenshot(path)
    