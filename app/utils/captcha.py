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
        

    
        
        
    

