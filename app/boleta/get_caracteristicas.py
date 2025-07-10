#!/usr/bin/env python3
import argparse
import os
import json
from datetime import datetime
from dotenv import load_dotenv

# Importaciones de las dependencias del proyecto
# Asegúrate de que estas rutas sean correctas o que el PYTHONPATH esté configurado
from app.utils.chromedriver import get_driver
from app.utils.pdfplumber import get_caracteristicas_vehiculo

load_dotenv()

def main():
    parser = argparse.ArgumentParser(description="Obtener información de boleta informativa.")
    parser.add_argument("--path", type=str, required=True, help="Ruta del archivo PDF de la boleta.")

    args = parser.parse_args()

    fecha = datetime.now()
    fecha_personalizado = fecha.strftime("%Y-%m-%d")

    """ quitar /apipy/download de path_pdf_boleta """
    if args.path.startswith("/apipy/download"):
        args.path = args.path.replace("/apipy/download", "")
        
    path_pdf_boleta = args.path
    
    driver = None
    try:

        caracteristicas = get_caracteristicas_vehiculo(path_pdf_boleta)

        result = {
            "caracteristicas": caracteristicas if caracteristicas is not None else "null",
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