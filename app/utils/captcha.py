from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import base64
from PIL import Image, ImageDraw, ImageFont
import io
from twocaptcha import TwoCaptcha
import time
from datetime import datetime


def get_captcha(img_captcha_base64, max_retries=5, delay=5):
    api_key = '91c5d78777ba4e8bc978a5d31d963b4f'
    solver = TwoCaptcha(api_key)

    for attempt in range(1, max_retries + 1):
        try:
            result = solver.normal(img_captcha_base64)
            captcha_text = result['code']
            print('Captcha resuelto:', captcha_text)
            return captcha_text

        except Exception as e:
            print(f'Error al resolver captcha en intento #{attempt}: {e}')
            if attempt < max_retries:
                print(f'Esperando {delay} segundos antes del próximo intento...')
                time.sleep(delay)
            else:
                print('Se alcanzó el número máximo de intentos. No se pudo resolver el captcha.')
                return '000000'  # Devuelve None si falla todos los intentos
        

    
        
        
def get_turnstile_token(ts_data, api_key, max_retries=5, delay=5):
    solver = TwoCaptcha(api_key)
    task_data = {
        'sitekey': ts_data['websiteKey'],
        'url': ts_data['websiteURL'],
    }
    if ts_data.get("action"):
        task_data["action"] = ts_data["action"]
    if ts_data.get("data"):
        task_data["data"] = ts_data["data"]
    if ts_data.get("userAgent"):
        task_data["userAgent"] = ts_data["userAgent"]

    for attempt in range(1, max_retries + 1):
        try:
            print(f"🎯 Resolviendo captcha (intento #{attempt})...")
            result = solver.turnstile(**task_data)
            token = result['code']
            print("✅ Token resuelto:", token)
            return token
        except Exception as e:
            print(f'⚠️ Error al resolver captcha: {e}')
            if attempt < max_retries:
                print(f'⏳ Reintentando en {delay}s...')
                time.sleep(delay)
            else:
                raise Exception("❌ No se pudo resolver el captcha tras varios intentos.")


