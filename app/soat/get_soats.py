#!/usr/bin/env python3
import argparse
import os
import json
from datetime import datetime
from dotenv import load_dotenv

# Importaciones de las dependencias del proyecto
# Asegúrate de que estas rutas sean correctas o que el PYTHONPATH esté configurado
from app.utils.chromedriver import get_driver
from app.utils.utils import get_soats

load_dotenv()

def main():
    parser = argparse.ArgumentParser(description="Obtener información de boleta informativa.")
    parser.add_argument("--placa", type=str, required=True, help="Número de placa del vehículo.")
    parser.add_argument("--idplacahistory", type=str, required=True, help="ID del historial de placa.")

    args = parser.parse_args()

    fecha = datetime.now()
    fecha_personalizado = fecha.strftime("%Y-%m-%d")

    user = os.getenv("USER_SYSTEM_BALANCE")
    password = os.getenv("PASSWORD_SYSTEM_BALANCE")

    placa = args.placa.upper()
    idplacahistory = args.idplacahistory
    path = f"/var/www/commands-placa/soats/{placa}/{fecha_personalizado}/{idplacahistory}"
    os.makedirs(path, exist_ok=True)
    
    driver = None
    try:
        driver = get_driver(placa, idplacahistory, path)

        message, soats = get_soats(placa, "https://www.soat.com.pe/servicios-soat/", driver, idplacahistory, path)
        result = {
            "message": message,
            "soats": soats if soats else "null"
        }
        print(json.dumps(result))

    except Exception as e:
        print(json.dumps({"error": str(e)}, indent=4))
        exit(1) # Salir con código de error
    finally:
        if driver:
            driver.quit()

if __name__ == "__main__":
    main()