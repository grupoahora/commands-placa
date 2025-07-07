import re
import pdfplumber
import glob


def get_caracteristicas_vehiculo(path_pdf):
    """
    Extrae las características del vehículo del PDF.
    """
    # Abrir el PDF y extraer texto
    
    texto = ""
    try:
        
        with pdfplumber.open(path_pdf) as pdf:  
            for page in pdf.pages:
                texto += page.extract_text() + "\n"


        caracteristicas = []
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
    except StopIteration:
            print("No se encontró ningún archivo PDF en la carpeta.")

def get_propietarios(path_pdf):
    """
    Extrae nombre, dirección, tipo de documento y número desde un PDF.
    """
    propietarios = []

    try:
        texto = ""
        with pdfplumber.open(path_pdf) as pdf:
            for page in pdf.pages:
                texto += page.extract_text() + "\n"

        # Dividir el texto por líneas limpias
        lineas = [line.strip() for line in texto.splitlines() if line.strip()]

        for i in range(len(lineas)):
            if lineas[i].startswith("Nombre :") and i + 1 < len(lineas) and lineas[i+1].startswith("Dirección :"):
                nombre_raw = lineas[i].replace("Nombre :", "").strip()
                direccion_raw = lineas[i+1].replace("Dirección :", "").strip()

                # Tipo de documento desde el final del nombre
                match_tipo = re.search(r"\b(DNI|CE|PARTIDA|[A-Z]{2,})\b$", nombre_raw)
                tipo_documento = match_tipo.group(1) if match_tipo else ""
                nombre = re.sub(r"\b(DNI|CE|PARTIDA|[A-Z]{2,})\b$", "", nombre_raw).strip()

                # Número de documento al final de la dirección
                match_nro = re.search(r"(\d{7,9})$", direccion_raw)
                numero_documento = match_nro.group(1) if match_nro else ""
                direccion = re.sub(r"\s*\d{7,9}$", "", direccion_raw).strip()

                propietarios.append({
                    "nombre": nombre,
                    "direccion": direccion,
                    "tipo_documento": tipo_documento,
                    "numero_documento": numero_documento
                })

        return propietarios

    except Exception as e:
        print(f"Error al procesar el PDF: {e}")
        return []
def get_afectaciones(path_pdf):
    """
    Extrae las afectaciones del PDF.
    """
    texto = ""
    # Ruta con comodín

    try:
    
        with pdfplumber.open(path_pdf) as pdf:  
            for page in pdf.pages:
                texto += page.extract_text() + "\n"

        # Extraer texto de cada página y filtrar los datos de propietarios
        data = []
    

        if "NO REGISTRA AFECTACIONES" in texto:
            # Usar expresiones regulares para extraer las validaciones
            data = False
        else:

            afectaciones = re.findall(r"Afectación\s*:\s*(.*?)(?=\s*Juzgado)", texto)
            expedientes = re.findall(r"Expediente\s*:\s*(\S*)(\S*)", texto)
            fechasAfectaciones = re.findall(r"Fecha Afec\s*:\s*(.*?)(?=\s*Secr. Juzga)", texto)
            juezs = re.findall(r"Juez\s*:\s*(.*?)(?=\s*Causal)", texto)
            emisorDescs = re.findall(r"Emisor Desc\s*:\s*(.*?)(?=\s*Doc. Desc)", texto)
            juzgados = re.findall(r"Juzgado\s*:\s*(\S*)(\S*)", texto)
            secrJuzgas = re.findall(r"Secr. Juzga\s*:\s*(\S*)(\S*)", texto)
            causals = re.findall(r"Causal\s*:\s*(\S*)(\S*)", texto)
            docDescs = re.findall(r"Doc. Desc\s*:\s*(\S*)(\S*)", texto)
            # Usar expresiones regulares para extraer las afectaciones
            # Agrupar los datos extraídos
            for i, afectacion in enumerate(afectaciones):
                expediente = expedientes[i]
                fechaAfectacion = fechasAfectaciones[i]
                juez = juezs[i]
                emisorDesc = emisorDescs[i]
                juzgado = juzgados[i]
                secrJuzga = secrJuzgas[i]
                causal = causals[i]
                docDesc = docDescs[i]
                data.append({
                    "afectacion": afectacion.strip(),
                    "expediente": expediente[0].strip(),
                    "fechaAfectacion": fechaAfectacion.strip(),
                    "juez": juez.strip(),
                    "emisorDesc": emisorDesc.strip(),
                    "juzgado": juzgado[0].strip(),
                    "secrJuzga": secrJuzga[0].strip(),
                    "causal": causal[0].strip(),
                    "docDesc": docDesc[0].strip(),
                })

        print(data)
        return data
    except StopIteration:
        print("No se encontró ningún archivo PDF en la carpeta.")