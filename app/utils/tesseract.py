import re
from pdf2image import convert_from_path
import pytesseract
from PIL import Image, ImageFilter, ImageEnhance
import json

pytesseract.pytesseract.tesseract_cmd = '/usr/bin/tesseract'
def get_data_consulta_vehicular(image_path_consulta):
    try:
        image = Image.open(image_path_consulta)
        custom_config = r'--psm 6' 
        text = pytesseract.image_to_string(image, lang='spa', config=custom_config)
        lines = text.splitlines()
        data = {
            'placa': '',
            'serie': '',
            'vin': '',
            'motor': '',
            'color': '',
            'marca': '',
            'modelo': '',
            'placa_vigente': '',
            'placa_anterior': '',
            'estado': '',
            'anotaciones': '',
            'sede': '',
            'anio_de_modelo': '',
            'propietarios': []
        }

        # Función auxiliar para buscar por llave y capturar valor en misma línea o la siguiente
        def get_value(label):
            for i, line in enumerate(lines):
                if label in line.upper():
                    # Buscar con expresión regular en la misma línea
                    match = re.search(rf"{label}[:]*\s*(\S.+)", line, re.IGNORECASE)
                    if match:
                        return match.group(1).strip()
                    # Si no hay valor en la misma línea, intenta en la siguiente
                    elif i + 1 < len(lines):
                        next_line = lines[i + 1].strip()
                        if next_line and not any(x in next_line.upper() for x in ['PLACA', 'SERIE', 'VIN', 'MOTOR', 'COLOR', 'MARCA', 'MODELO', 'ESTADO', 'ANOTACIONES', 'SEDE', 'AÑO']):
                            return next_line
            return ''

        # Extraer todos los valores
        data['placa'] = get_value('PLACA')
        data['serie'] = get_value('SERIE')
        data['vin'] = get_value('VIN')
        data['motor'] = get_value('MOTOR')
        data['color'] = get_value('COLOR')
        data['marca'] = get_value('MARCA')
        data['modelo'] = get_value('MODELO')
        data['placa_vigente'] = get_value('PLACA VIGENTE')
        data['placa_anterior'] = get_value('PLACA ANTERIOR')
        data['estado'] = get_value('ESTADO')
        data['anotaciones'] = get_value('ANOTACIONES')
        data['sede'] = get_value('SEDE')
        data['anio_de_modelo'] = get_value('AÑO DE MODELO')

        # Buscar propietarios desde su encabezado hasta antes de la fecha o línea vacía
        prop_start = next((i for i, line in enumerate(lines) if 'PROPIETARIO' in line.upper()), None)
        if prop_start is not None:
            propietarios = []
            for line in lines[prop_start + 1:]:
                if re.search(r'\d{2}/\d{2}/\d{4}', line):  # si llega a una fecha, parar
                    break
                if line.strip():
                    propietarios.append(line.strip())
            data['propietarios'] = propietarios

        return [data]

    except Exception as e:
        print(f"Error: {e}")
        raise e

def get_propietarios(images):

   

    # Extraer texto de cada página y filtrar los datos de propietarios
    propietarios = []
    for image in images:
        # Extraer texto de la imagen
        texto = pytesseract.image_to_string(image, lang="spa")
        
        # Buscar la sección "Datos del Propietario"
        if "Datos del Propietario" in texto:
            # Usar expresiones regulares para extraer nombres y direcciones
            nombres = re.findall(r"Nombre\s*:\s*(.*?)(?=\s*DNI)", texto)
            direcciones_y_dnis = re.findall(r"Dirección\s*:\s*(.*?)\s+(\d{7,8})", texto)
            
            # Agrupar los datos extraídos
            for i, nombre in enumerate(nombres):
                direccion, dni = direcciones_y_dnis[i]
                propietarios.append({
                    "nombre": nombre.strip(),
                    "direccion": direccion.strip(),
                    "dni": dni.strip()
                })

    return propietarios



def get_captcha_tesseract(image_path_consulta):
    try:

        image = Image.open(image_path_consulta)
        # Convertir a escala de grises
        image = image.convert("L")

        # Aumentar el contraste
        enhancer = ImageEnhance.Contrast(image)
        image = enhancer.enhance(2)
          # Ajusta el factor de contraste según sea necesario
        """ image = image.resize((int(image.width * 1.5), int(image.height * 1.5)), Image.Resampling.LANCZOS) """
        # Aplicar un filtro para reducir el ruido
        image = image.filter(ImageFilter.MedianFilter(size=3))

        # Guardar la imagen preprocesada (opcional, para verificar el resultado)
        image.save("preprocessed_captcha.png")
        # Configurar pytesseract para solo reconocer números
        custom_config = r'--psm 6 -c tessedit_char_whitelist=0123456789'

        # Aplicar OCR para extraer el texto (solo números)
        text1 = pytesseract.image_to_string(image, config=custom_config, lang='spa')
        image2 = image.resize((int(image.width * 1.5), int(image.height * 2)), Image.Resampling.LANCZOS)
        image2.save("preprocessed_captcha2.png")
        text2 = pytesseract.image_to_string(image2, config=custom_config, lang='spa')
        image3 = image.resize((int(image.width * 1.5), int(image.height * 3)), Image.Resampling.LANCZOS)
        image3.save("preprocessed_captcha3.png")
        text3 = pytesseract.image_to_string(image3, config=custom_config, lang='spa')

        print("text1",text1.strip())
        print("text2",text2.strip())
        print("text3",text3.strip())

        intentos = 0
        max_intentos = 5
        while intentos < max_intentos:

            if text1.strip() != text2.strip()  or text2.strip() != text3.strip() or text1.strip() != text3.strip() or text1.strip() == "" or len(text1.strip()) != 6:
                text1 = pytesseract.image_to_string(image, config=custom_config, lang='spa')
                image2 = image2.resize((int(image2.width * 1.05), int(image2.height * 1.05)), Image.Resampling.LANCZOS)
                image2.save("preprocessed_captcha2.png")
                text2 = pytesseract.image_to_string(image2, config=custom_config, lang='spa')
                image3 = image3.resize((int(image3.width * 1.05), int(image3.height * 1.05)), Image.Resampling.LANCZOS)
                image3.save("preprocessed_captcha3.png")
                text3 = pytesseract.image_to_string(image3, config=custom_config, lang='spa')
                print("text1",text1.strip())
                print("text2",text2.strip())
                print("text3",text3.strip())
               
            
                intentos += 1
            else:
                text = text1
                return text.strip()

        return False    
        
    except Exception as e:
        print(f"Error: {e}")
        raise e


def get_caracteristicas_vehiculo(images):
    """
    Extrae las características del vehículo de las imágenes del PDF.
    """
    caracteristicas = []
    for image in images:
        # Extraer texto de la imagen
        texto = pytesseract.image_to_string(image, lang="spa")
        
        caracteristicas.append({
            'placa': re.search(r'Placa :\s*(\S*)(\S*)', texto).group(1).strip(),
            'tipo_uso': re.search(r'Tipo Uso :\s*(.*?)(?=\s*N°)', texto).group(1),
            'catagoria': re.search(r'Categoría :\s*(\S*)(\S*)', texto).group(1).strip(),
            'carroceria': re.search(r'Carrocería :\s*(.*?)(?=\s*N°)', texto).group(1).strip(),
            'marca': re.search(r'Marca :\s*(\S*)(\S*)', texto).group(1).strip(),
            'modelo': re.search(r'Modelo :\s*(\S*)(\S*)', texto).group(1).strip(),
            'ano_mod': re.search(r'Año Mod :\s*(.*?)(?=\s*N°)', texto).group(1).strip(),
            'ano_fab': re.search(r'Año Fab :\s*(.*?)(?=\s*Cilindrada)', texto).group(1).strip(),
            'n_version': re.search(r'N° Versión :\s*(.*?)(?=\s*Peso)', texto).group(1).strip(),
            'n_serie': re.search(r'N° Serie :\s*(.*?)(?=\s*Peso)', texto).group(1).strip(),
            'n_vin': re.search(r'N° de VIN :\s*(.*?)(?=\s*Carga)', texto).group(1).strip(),
            'color_1': re.search(r'Color 1 :\s*(.*?)(?=\s*N°)', texto).group(1).strip(),
            'color_2': re.search(r'Color 2 :\s*(.*?)(?=\s*N°)', texto).group(1).strip(),
            'oficina': re.search(r'OFICINA\s*(\S*)(\S*)', texto).group(1).strip(),
            'color_3': re.search(r'Color 3 :\s*(\S*)(\S*)', texto).group(1).strip(),
            'n_motor': re.search(r'N° Motor :\s*(.*?)(?=\s*N°)', texto).group(1).strip(),
            'tipo_combus': re.search(r'Tipo Combus :\s*(.*?)(?=\s*N°)', texto).group(1).strip(),
            'pot_motor': re.search(r'Pot. Motor :\s*(.*?)(?=\s*Longitud)', texto).group(1).strip(),
            'n_cilindros': re.search(r'N° Cilindros :\s*(.*?)(?=\s*Ancho)', texto).group(1).strip(),
            'cilindrada': re.search(r'Cilindrada :\s*(.*?)(?=\s*Altura)', texto).group(1).strip(),
            'peso_neto': re.search(r'Peso Neto :\s*(.*?)(?=\s*Form)', texto).group(1).strip(),
            'peso_bruto': re.search(r'Peso Bruto :\s*(.*?)(?=\s*Inmatriculac.)', texto).group(1).strip(),
            'carga_util': re.search(r'Carga Útil :\s*(.*?)(?=\s*Fec.)', texto).group(1).strip(),
            'n_asientos': re.search(r'N° Asientos :\s*(.*?)(?=\s*Condición)', texto).group(1).strip(),
            'n_pasajeros': re.search(r'N° Pasajer. :\s*(\S*)(\S*)', texto).group(1).strip(),
            'n_partida': re.search(r'N° Partida :\s*(.*)', texto).group(1),
            'n_ejes': re.search(r'N° Ejes :\s*(.*)', texto).group(1),
            'n_ruedas': re.search(r'N° Ruedas :\s*(.*)', texto).group(1),
            'longitud': re.search(r'Longitud :\s*(.*)', texto).group(1),
            'ancho': re.search(r'Ancho :\s*(.*)', texto).group(1),
            'altura': re.search(r'Altura :\s*(.*)', texto).group(1),
            'form_rodan': re.search(r'Form. Rodan. :\s*(.*)', texto).group(1),
            'inmatriculac': re.search(r'Inmatriculac. :\s*(.*)', texto).group(1),
            'fecha_prop': re.search(r'Fec. Prop :\s*(.*)', texto).group(1),
            'condicion': re.search(r'Condición :\s*(.*)', texto).group(1),
    
            
        })

    return caracteristicas