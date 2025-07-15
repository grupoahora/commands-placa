#!/usr/bin/env python3
import argparse
import os
import json
from datetime import datetime
from dotenv import load_dotenv

# Importaciones de las dependencias del proyecto
# Asegúrate de que estas rutas sean correctas o que el PYTHONPATH esté configurado
from app.utils.chromedriver import get_driver
from app.utils.utils import get_multas

load_dotenv()

def main():
    parser = argparse.ArgumentParser(description="Obtener información de boleta informativa.")
    parser.add_argument("--idplacahistory", type=str, required=True, help="ID del historial de placa.")
    parser.add_argument("--numero_documento", type=str, required=True, help="Número de documento")
    args = parser.parse_args()

    fecha = datetime.now()
    fecha_personalizado = fecha.strftime("%Y-%m-%d")

    user = os.getenv("USER_SYSTEM_BALANCE")
    password = os.getenv("PASSWORD_SYSTEM_BALANCE")

    idplacahistory = args.idplacahistory
    numero_documento = args.numero_documento
    path = f"/var/www/laravelplacas/public/multas/{numero_documento}/{fecha_personalizado}/{idplacahistory}"
    os.makedirs(path, exist_ok=True)
    
    driver = None
    try:
        driver = get_driver(numero_documento, idplacahistory, path)

        message, multas = get_multas(numero_documento, idplacahistory, driver, 'https://multas.jne.gob.pe/login', path)

        
        result = {
            "message": message,
            "multas": multas if multas is not None else "null"
        }   
        # Imprimir el resultado en formato JSON
        print(json.dumps(result))

    except Exception as e:
        print(json.dumps({"error": str(e)}, indent=4))
        exit(1) # Salir con código de error
    finally:
        if driver:
            driver.quit()

if __name__ == "__main__":
    main()