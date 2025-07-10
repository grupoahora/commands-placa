#!/usr/bin/env python3
import argparse
import os
import json
from datetime import datetime
from dotenv import load_dotenv

# Importaciones de las dependencias del proyecto
# Asegúrate de que estas rutas sean correctas o que el PYTHONPATH esté configurado
from app.utils.chromedriver import get_driver
from app.utils.utils import get_asientos

load_dotenv()

def main():
    parser = argparse.ArgumentParser(description="Obtener información de boleta informativa.")
    parser.add_argument("--placa", type=str, required=True, help="Número de placa del vehículo.")
    parser.add_argument("--idplacahistory", type=str, required=True, help="ID del historial de placa.")
    parser.add_argument("--oficina", type=str, default="LIMA", help="Oficina de registro (default: LIMA).")
    args = parser.parse_args()

    fecha = datetime.now()
    fecha_personalizado = fecha.strftime("%Y-%m-%d")

    user = os.getenv("USER_SYSTEM_BALANCE")
    password = os.getenv("PASSWORD_SYSTEM_BALANCE")

    placa = args.placa.upper()
    idplacahistory = args.idplacahistory
    oficina = args.oficina
    path = f"/var/www/commands-placa/asientos/{placa}/{fecha_personalizado}/{idplacahistory}"
    os.makedirs(path, exist_ok=True)
    
    driver = None
    try:
        driver = get_driver(placa, idplacahistory, path)

        message, asientos = get_asientos(user, password, placa, 'https://sprl.sunarp.gob.pe/sprl/ingreso', driver, idplacahistory, path, oficina)
        
        result = {
            "message": message,
            "asientos": asientos if asientos is not None else "null"
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