from app.utils.boleta import login_balance, get_balance
from app.utils.chromedriver import find_element_by, take_screenshot,get_driver, wait_for_page_load, wait_attr_by_find_element, wait_for_page_load_complete
from app.utils.tesseract import get_data_consulta_vehicular, get_captcha_tesseract
from app.utils.pdfplumber import get_caracteristicas_vehiculo, get_propietarios, get_afectaciones
from app.utils.captcha import get_captcha, get_turnstile_token
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from datetime import datetime

# WebDriverWait
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import base64
from PIL import Image, ImageDraw, ImageFont
import io
import os
import requests
from io import BytesIO
import json
from pdf2image import convert_from_path
import glob


from selenium.common.exceptions import NoSuchElementException, TimeoutException

def update_balance_boleta(user, password, url, driver):
    
    try:
        # Acceder a la URL
        driver.get(url)

        time.sleep(5)

        
        # Ejecutar un script para vaciar el contenido del div con clase cdk-overlay-container
        driver.execute_script("""
            let modal = document.querySelector('.cdk-overlay-container');
            if (modal && modal.innerHTML !== '') {
                modal.innerHTML = '';
            }
        """)

        # Buscar el botón con el span que contiene "INGRESAR" y hacer clic
        ingresar_button = find_element_by(driver, By.XPATH, "//button[.//span[text()='INGRESAR']]",5)
        ingresar_button.click()

       

        if login_balance(user, password, driver):

            balance = get_balance(driver)
            # Obtener la fecha y hora actuales
            fecha_hora_actual = datetime.now()
            # Mostrar la fecha y hora en un formato personalizado
            formato_personalizado = fecha_hora_actual.strftime("%Y-%m-%d %H:%M:%S")
            take_screenshot(driver, f"balance_boleta/_{user}_{formato_personalizado}.png")
            return balance
    except Exception as e:
        print(f"Error: {e}")
        raise e
    finally:
        driver.quit()

def get_boleta_informativa(user, password, placa, url, driver, idplacahistory, path):
    try:
        os.makedirs(path, exist_ok=True)
        # Acceder a la URL
        driver.get(url)

        
        time.sleep(5)

       
        # Ejecutar un script para vaciar el contenido del div con clase cdk-overlay-container
        driver.execute_script("""
            let modal = document.querySelector('.cdk-overlay-container');
            if (modal && modal.innerHTML !== '') {
                modal.innerHTML = '';
            }
        """)

        # Buscar el botón con el span que contiene "INGRESAR" y hacer clic
        ingresar_button = find_element_by(driver, By.XPATH, "//button[.//span[text()='INGRESAR']]",5)

        ingresar_button.click()
        if login_balance(user, password, driver):
            path = f"{path}/evidencias"
            os.makedirs(path, exist_ok=True)
            take_screenshot(driver, f"{path}/login_balance.png")

            current_url = driver.current_url
            driver.get('https://sprl.sunarp.gob.pe/sprl/main/solicitar-boleta-vehiculo')
            # Esperar a que la nueva página cargue
            wait_for_page_load(driver, current_url)
            
            take_screenshot(driver, f"{path}/solicitar-boleta-vehiculo.png")
            input_placa = find_element_by(driver, By.CLASS_NAME, 'input-form',5)
            input_placa.send_keys(placa)
            button_buscar = find_element_by(driver, By.CLASS_NAME, 'Buscar',5)
            button_buscar.click()
            time.sleep(5)
            # Esperar a que la tabla esté presente
            table_element = find_element_by(driver, By.TAG_NAME, 'table', 5)
            # Hacer scroll hasta el elemento de la tabla
            driver.execute_script("arguments[0].scrollIntoView();", table_element)
            button_get_boleta_pdf = find_element_by(driver, By.CLASS_NAME, 'button-form',5)
            button_get_boleta_pdf.click()
            time.sleep(5)
            button_aceptar_descarga = find_element_by(driver, By.XPATH, "//span[contains(text(), 'Aceptar')]",5)
            button_aceptar_descarga.click()
            time.sleep(5)

            # Obtener la fecha y hora actuales
            fecha_hora_actual = datetime.now()
            formato_personalizado = fecha_hora_actual.strftime("%Y-%m-%d")
            message = ''
            propietarios = caracteristicas = afectaciones = None

            try:
                # Verifica si aparece el mensaje de saldo insuficiente
                find_element_by(driver, By.XPATH, "//span[contains(text(), 'no tiene el saldo suficiente')]", 5)
                message = 'No tiene el saldo suficiente para descargar la boleta'
                try:
                    path_pdf_boleta = f"{path}/*.pdf"
                    path_pdf_boleta = next(glob.iglob(path_pdf_boleta))
                    
                    

                    message = 'Boleta informativa descargada con éxito'

                except StopIteration:
                    message = 'No se encontró el archivo PDF de la boleta'
            except (TimeoutException, NoSuchElementException):
                # Si no aparece el mensaje de saldo insuficiente, se asume que el PDF fue generado correctamente
                try:
                    path_pdf_boleta = f"{path}/*.pdf"
                    path_pdf_boleta = next(glob.iglob(path_pdf_boleta))
                    
                    

                    message = 'Boleta informativa descargada con éxito'

                except StopIteration:
                    message = 'No se encontró el archivo PDF de la boleta'


        return message, path_pdf_boleta, propietarios, afectaciones
    
        
    except Exception as e:
        print(f"Error: {e}")
        raise e
def get_consulta_vehicular(placa, idplacahistory, url, driver, path):
    try:

        # Acceder a la URL
        driver.get(url)
        time.sleep(15)
        # Buscar la img con el id "image" con el attr "src" y esperar a que esté presente la imagen del captcha en el attr "src"
        img_captcha = find_element_by(driver, By.ID, 'image', 5)
        wait_attr_by_find_element(driver, img_captcha, "src", 5)

        # Obtener la imagen como un PNG binario
        captcha_png = img_captcha.screenshot_as_png
        captcha_image = Image.open(io.BytesIO(captcha_png))
        # mover captcha_image to folder captchas/{placa}/{idplacahistory} si no existe crear el folder y borrar el original
        path_captchas = f"{path}/evidencias/captchas"
        # Asegurar que el directorio existe
        os.makedirs(path_captchas, exist_ok=True)

        # Guardar la imagen del captcha
        captcha_image.save(f"{path_captchas}/captcha_one.png", format="PNG")


        # Convertir la imagen a base64 para enviar a 2Captcha
        buffered = io.BytesIO(captcha_png)
        captcha_image.save(buffered, format="PNG")
        img_base64 = base64.b64encode(buffered.getvalue()).decode("utf-8")

        # obtener el texto del captcha
        captcha_text1 = get_captcha(f"{path_captchas}/captcha_one.png")
        
        captcha_text = captcha_text1
        # Ingresar el texto resuelto en el campo del captcha con id "codigoCaptcha"
        input_captcha = find_element_by(driver, By.ID, 'codigoCaptcha', 5)
        input_captcha.clear()
        for char in captcha_text:
            input_captcha.send_keys(char)

        # Ingresar la placa en el campo con id "nroPlaca"
        input_placa = find_element_by(driver, By.ID, 'nroPlaca', 5)
        input_placa.clear()
        input_placa.send_keys(placa)

        # Esperar 2 segundos después de escribir el captcha
        time.sleep(2)

        # Buscar el botón con la clase 'ant-btn' y hacer clic 
        button_consultar = find_element_by(driver, By.CLASS_NAME, 'ant-btn', 5)
        button_consultar.click()

        # Esperar 5 segundos después de hacer click()
        time.sleep(5)
        button_ok_off_captcha = find_element_by(driver, By.XPATH, "//button[contains(text(), 'OK')]", 5)
        while button_ok_off_captcha:
            # Hacer clic en el botón
            button_ok_off_captcha.click()
            time.sleep(5)
            # Obtener la imagen como un PNG binario
            captcha_png = img_captcha.screenshot_as_png
            captcha_image = Image.open(io.BytesIO(captcha_png))
            # mover captcha_image to folder captchas/{placa}/{idplacahistory} si no existe crear el folder y borrar el original
            # Asegurar que el directorio existe
            os.makedirs(path_captchas, exist_ok=True)

            # Guardar la imagen del captcha
            captcha_image.save(f"{path_captchas}/captcha_one.png", format="PNG")


            # Convertir la imagen a base64 para enviar a 2Captcha
            buffered = io.BytesIO(captcha_png)
            captcha_image.save(buffered, format="PNG")
            img_base64 = base64.b64encode(buffered.getvalue()).decode("utf-8")

            # obtener el texto del captcha
            captcha_text1 = get_captcha(f"{path_captchas}/captcha_one.png")
            
            captcha_text = captcha_text1
            # Ingresar el texto resuelto en el campo del captcha con id "codigoCaptcha"
            input_captcha = find_element_by(driver, By.ID, 'codigoCaptcha', 5)
            input_captcha.clear()
            for char in captcha_text:
                input_captcha.send_keys(char)

            # Ingresar la placa en el campo con id "nroPlaca"
            input_placa = find_element_by(driver, By.ID, 'nroPlaca', 5)
            input_placa.clear()
            input_placa.send_keys(placa)

            # Esperar 2 segundos después de escribir el captcha
            time.sleep(2)

            # Buscar el botón con la clase 'ant-btn' y hacer clic 
            button_consultar = find_element_by(driver, By.CLASS_NAME, 'ant-btn', 5)
            button_consultar.click()

            # Esperar 5 segundos después de hacer click()
            time.sleep(5)
            button_ok_off_captcha = find_element_by(driver, By.XPATH, "//button[contains(text(), 'OK')]", 5)
            
        # Esperar a que la página esté completamente cargada
        wait_for_page_load_complete(driver)

        # Obtener la fecha y hora actuales
        fecha_hora_actual = datetime.now()
        # Mostrar la fecha y hora en un formato personalizado
        formato_personalizado = fecha_hora_actual.strftime("%Y-%m-%d")
        
        # Crear path donde se guardará la captura de pantalla
        path_capturas_consulta_vehicular = f"{path}"
        os.makedirs(path_capturas_consulta_vehicular, exist_ok=True)
        
        # Obtener img dentro de element app-form-datos-consulta
        app_form_datos_consulta = find_element_by(driver, By.TAG_NAME, 'app-form-datos-consulta', 5)
        # Hacer scroll hasta el elemento 
        driver.execute_script("arguments[0].scrollIntoView();", app_form_datos_consulta)
        # Obtener img de app-form-datos-consulta
        img = app_form_datos_consulta.find_element(By.TAG_NAME, 'img')  
        img_consulta_vehicular = img.screenshot_as_png
        img_consulta_vehicular = Image.open(io.BytesIO(img_consulta_vehicular))
        img_consulta_vehicular.save(f"{path_capturas_consulta_vehicular}/evidencias/consulta.png", format="PNG")
        
        
        
        

        # Agregar fecha y hora a la captura de pantalla
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        image = Image.open(f"{path_capturas_consulta_vehicular}/evidencias/consulta.png")
        draw = ImageDraw.Draw(image)

        # Configurar fuente y tamaño; puedes usar una fuente predeterminada si `ImageFont.truetype` no funciona
        try:
            font = ImageFont.truetype("arial.ttf", 40)  # Tamaño de letra aumentado
        except IOError:
            font = ImageFont.load_default()

        # Calcular posición en la esquina superior derecha
        text_position = (image.width - 400, 10)  # Ajusta según sea necesario para alineación correcta
        draw.text(text_position, timestamp, fill="black", font=font)
        image.save(f"{path_capturas_consulta_vehicular}/evidencias/consulta.png", format="PNG")

        image_path_consulta = f"{path_capturas_consulta_vehicular}/evidencias/consulta.png"
        message = 'Consulta vehicular realizada con exito'
        data_consulta_vehicular = get_data_consulta_vehicular(image_path_consulta)
        return message, image_path_consulta, data_consulta_vehicular
    except Exception as e:
        print(f"Error: {e}")
        raise e
    
def get_revision_tecnica_data(placa, text):
    # realizar peticion post fetch a ruta "https://portal.mtc.gob.pe/reportedgtt/form/frmConsultaPlacaITV.aspx/refrescarCaptcha" y guardar de response el response.d 
    # URL a la que se realizará la solicitud POST
    url = "https://portal.mtc.gob.pe/reportedgtt/form/frmConsultaPlacaITV.aspx/getPlaca"

    # Encabezados de la solicitud (pueden variar según lo que necesites)
    headers = {
        "Content-Type": "application/json; charset=utf-8",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
    }

    # Cuerpo de la solicitud (puede variar según lo que necesites)
    payload = json.dumps({"ose1":"1", "ose2": placa, "ose3": text})

    # Realizar la solicitud POST
    response = requests.post(url, data=payload, headers=headers)
    # Verificar si la solicitud fue exitosa
    if response.status_code == 200:
        # Convertir la respuesta a JSON
        response_json = response.json()
        
        # Obtener el valor de 'd' de la respuesta
        d_value = response_json.get('d')
        return d_value
    else:
        print(f"Error en la solicitud: {response.status_code}")
        print(response.text)
def get_revision_tecnica(placa, url, driver, idplacahistory, path):

    try:
        # Acceder a la URL
        driver.get(url)
        time.sleep(15)
        # Buscar la img con el id "image" con el attr "src" y esperar a que esté presente la imagen del captcha en el attr "src"
        img_captcha = find_element_by(driver, By.ID, 'imgCaptcha', 5)
        wait_attr_by_find_element(driver, img_captcha, "src", 5)
        
        # Obtener el atributo src de la imagen del captcha
        src_captcha = img_captcha.get_attribute("src")
        """ print(src_captcha) """
        # Obtener el valor base64 de la imagen del captcha
        img_captcha_replace = src_captcha.replace('data:image/jpeg;base64,','')
        # Decodificar la cadena Base64
        img_captcha_decode = base64.b64decode(img_captcha_replace)
        # Crear una imagen a partir de los datos decodificados
        image = Image.open(BytesIO(img_captcha_decode))
        image.convert("RGB")
        path_captchas = f"{path}/evidencias/captchas"
        if not os.path.exists(path_captchas):
            os.makedirs(path_captchas)
            image.save(f"{path_captchas}/captcha_one.png", format="PNG")
        else:
            image.save(f"{path_captchas}/captcha_one.png", format="PNG")

        # Guardar la imagen en formato PNG
        
        text = get_captcha_tesseract(f"{path_captchas}/captcha_one.png")
        
        while text == False:
            # Buscar el botón con el span que contiene "INGRESAR" y hacer clic
            new_captcha_btn = find_element_by(driver, By.ID, "btnCaptcha",5)
            new_captcha_btn.click()
            time.sleep(5)
            # Obtener el atributo src de la imagen del captcha
            src_captcha = img_captcha.get_attribute("src")
            # Obtener el valor base64 de la imagen del captcha
            img_captcha_replace = src_captcha.replace('data:image/jpeg;base64,','')
            # Decodificar la cadena Base64
            img_captcha_decode = base64.b64decode(img_captcha_replace)
            # Crear una imagen a partir de los datos decodificados
            image = Image.open(BytesIO(img_captcha_decode))
            image.convert("RGB")
            path_captchas = f"{path}/evidencias/captchas"
            if not os.path.exists(path_captchas):
                os.makedirs(path_captchas)
                image.save(f"{path_captchas}/captcha_one.png", format="PNG")
            else:
                image.save(f"{path_captchas}/captcha_one.png", format="PNG")
            text = get_captcha_tesseract(f"{path_captchas}/captcha_one.png")
        raw = {
            "ose1": "1",
            "ose2": placa,
            "ose3": text
        }
        driver.execute_script(f"""
            const myHeaders = new Headers();
            myHeaders.append("Content-Type", "application/json");
            myHeaders.append("Cookie", "ASP.NET_SessionId=oyqbnbtoyjvivnz2ikgfggi2");

            const raw = JSON.stringify({raw});

            const inputElement = document.createElement("input");
            inputElement.id = "input-data";
            const requestOptions = {{
                method: "POST",
                headers: myHeaders,
                body: raw,
                redirect: "follow"
            }};

            fetch("https://portal.mtc.gob.pe/reportedgtt/form/frmConsultaPlacaITV.aspx/getPlaca", requestOptions)
                .then((response) => response.text())
                .then((result) => {{
                    inputElement.dataset.value = result;
                    document.body.appendChild(inputElement);
                    console.log(result);
                }})
                .catch((error) => console.error(error));
        """)
        # Ingresar el texto resuelto en el campo del captcha con id "codigoCaptcha"
        time.sleep(5)
        input_data = find_element_by(driver, By.ID, 'input-data', 5)
        data = input_data.get_attribute("data-value")
        # Parsear la cadena JSON
        data = json.loads(data)
        # Acceder al diccionario interno
        inner_data_d = json.loads(data['d'])
        # Acceder a la lista de datos
        data_list = inner_data_d['DATA']
        return data_list
        
        # Esperar a que la tabla esté presente
        data = get_revision_tecnica_data(placa, text)
    except Exception as e:

        return {"error": str(e)}, 500

def get_multas(numero_documento, idplacahistory, driver, url, path):
    # Acceder a la URL
    driver.get(url)
    time.sleep(15)
    take_screenshot(driver, f"{path}/evidencias/open_page_multas.png")
    
    # Buscar el input con formcontrolname="numero_documento" usando find_element_by(driver, By.CSS_SELECTOR, 'input[formcontrolname="Dni"]', 5)
    input_dni = find_element_by(driver, By.CSS_SELECTOR, 'input[formcontrolname="Dni"]', 5)
    
    # Limpiar el campo de texto 
    input_dni.clear()
    # Ingresar el DNI en el campo de texto
    input_dni.send_keys(numero_documento)
    # Buscar la img con el id "image" con el attr "src" y esperar a que esté presente la imagen del captcha en el attr "src"
    img_captcha = find_element_by(driver, By.ID, 'imgcaptcha', 5)
    wait_attr_by_find_element(driver, img_captcha, "src", 5)
    
    # Obtener la imagen como un PNG binario
    captcha_png = img_captcha.screenshot_as_png
    captcha_image = Image.open(io.BytesIO(captcha_png))
    path_captchas = f"{path}/evidencias/captchas"
    # Asegurar que el directorio existe
    os.makedirs(path_captchas, exist_ok=True)

    # Guardar la imagen del captcha
    captcha_image.save(f"{path_captchas}/captcha_one.png", format="PNG")
    # obtener el texto del captcha
    captcha_text1 = get_captcha(f"{path_captchas}/captcha_one.png")
    print(captcha_text1)
    
    captcha_text = captcha_text1
    # Aquí se implementará la lógica para obtener las multas
    # Por ahora, solo retornamos un diccionario de ejemplo
    
    # Buscar el input con id="inpcaptcha" usando find_element_by(driver, By.ID, 'inpcaptcha', 5)
    input_captcha = find_element_by(driver, By.ID, 'inpcaptcha', 5)
    # Limpiar el campo de texto
    input_captcha.clear()
    # Ingresar el texto del captcha en el campo de texto
    input_captcha.send_keys(captcha_text)
    # buscar checkbox con id="ckbtermino" y hacer clic
    checkbox_terminos = find_element_by(driver, By.ID, 'ckbtermino', 5)
    checkbox_terminos.click()
    time.sleep(5)

    # buscar boton con el texto "Aceptar" en su interior para encontrarlo toca hacer scroll o hacer focus primero en el
    button_aceptar = find_element_by(driver, By.XPATH, "//button[contains(text(), 'Aceptar')]", 5)
    # Hacer focus en el botón (opción 2)
    ActionChains(driver).move_to_element(button_aceptar).perform()
    # Hacer clic en el botón   
    button_aceptar.click()
    time.sleep(5)
    # buscar boton con el id="btnConsultar" y hacer clic
    button_consultar = find_element_by(driver, By.ID, 'btnConsultar', 5)
    current_url = driver.current_url
    button_consultar.click()
    time.sleep(5)
    button_ok_off_captcha = find_element_by(driver, By.XPATH, "//button[contains(text(), 'OK')]", 5)
    while button_ok_off_captcha:
        # Hacer clic en el botón
        button_ok_off_captcha.click()
        time.sleep(5)
        # Buscar la img con el id "image" con el attr "src" y esperar a que esté presente la imagen del captcha en el attr "src"
        img_captcha = find_element_by(driver, By.ID, 'imgcaptcha', 5)
        wait_attr_by_find_element(driver, img_captcha, "src", 5)
        
        # Obtener la imagen como un PNG binario
        captcha_png = img_captcha.screenshot_as_png
        captcha_image = Image.open(io.BytesIO(captcha_png))
        # Asegurar que el directorio existe
        os.makedirs(path_captchas, exist_ok=True)

        # Guardar la imagen del captcha
        captcha_image.save(f"{path_captchas}/captcha_one.png", format="PNG")
        # obtener el texto del captcha
        captcha_text1 = get_captcha(f"{path_captchas}/captcha_one.png")
        print(captcha_text1)
        
        captcha_text = captcha_text1
        # Aquí se implementará la lógica para obtener las multas
        # Por ahora, solo retornamos un diccionario de ejemplo
        
        # Buscar el input con id="inpcaptcha" usando find_element_by(driver, By.ID, 'inpcaptcha', 5)
        input_captcha = find_element_by(driver, By.ID, 'inpcaptcha', 5)
        # Limpiar el campo de texto
        input_captcha.clear()
        # Ingresar el texto del captcha en el campo de texto
        input_captcha.send_keys(captcha_text)
        # buscar checkbox con id="ckbtermino" y hacer clic
        

        # buscar boton con el texto "Aceptar" en su interior para encontrarlo toca hacer scroll o hacer focus primero en el
        button_aceptar = find_element_by(driver, By.XPATH, "//button[contains(text(), 'Aceptar')]", 5)
        # Hacer focus en el botón (opción 2)
        ActionChains(driver).move_to_element(button_aceptar).perform()
        # Hacer clic en el botón   
        button_aceptar.click()
        time.sleep(5)
        # buscar boton con el id="btnConsultar" y hacer clic
        button_consultar = find_element_by(driver, By.ID, 'btnConsultar', 5)
        current_url = driver.current_url
        button_consultar.click()
        time.sleep(5)
        button_ok_off_captcha = find_element_by(driver, By.XPATH, "//button[contains(text(), 'OK')]", 5)
        
        
        
    
    
    # Esperar a que la nueva página cargue
    wait_for_page_load(driver, current_url)
    # Asegurar que el directorio existe
    os.makedirs(path_captchas, exist_ok=True)
    
    take_screenshot(driver, f"{path}/evidencias/resultado_multas.png")
    multas = []

    try:
        # Verificar si existe el mensaje "no cuenta con multas pendientes"
        message = "No cuenta con multas pendientes"
        mensaje_sin_multas = find_element_by(driver, By.XPATH, "//h5[contains(text(), 'no cuenta con multas pendientes')]", 3)
        if mensaje_sin_multas:
            return False, multas
    except:
        pass  # Si no lo encuentra
    
   
    # Buscar la tabla de multas
    tabla_multas = find_element_by(driver, By.XPATH, "//div[@id='multasPendientes']//table", 5)

    # Extraer todas las filas de la tabla
    filas = tabla_multas.find_elements(By.TAG_NAME, "tr")[1:]  # Omitimos la primera fila (encabezados)

    # Extraer los datos de la tabla
    message = "Multas pendientes encontradas"
    for fila in filas:
        celdas = fila.find_elements(By.TAG_NAME, "td")
        if len(celdas) >= 5:
            multa = {
                "codigo": celdas[0].text.strip(),
                "proceso_electoral": celdas[1].text.strip(),
                "tipo_omision": celdas[2].text.strip(),
                "deuda": celdas[3].text.strip(),
                "etapa_cobranza": celdas[4].text.strip(),
            }
            multas.append(multa)

    return message, multas


def get_asientos(user, password, placa, url, driver, idplacahistory, pathpdf, oficina = 'LIMA'):
    try:
        # Acceder a la URL
        driver.get(url)

        
        time.sleep(5)

       
        # Ejecutar un script para vaciar el contenido del div con clase cdk-overlay-container
        driver.execute_script("""
            let modal = document.querySelector('.cdk-overlay-container');
            if (modal && modal.innerHTML !== '') {
                modal.innerHTML = '';
            }
        """)

        # Buscar el botón con el span que contiene "INGRESAR" y hacer clic
        ingresar_button = find_element_by(driver, By.XPATH, "//button[.//span[text()='INGRESAR']]",5)

        ingresar_button.click()

        if login_balance(user, password, driver):
            current_url = driver.current_url
            take_screenshot(driver, f"{pathpdf}/evidencias/login_asientos.png")
            driver.get('https://sprl.sunarp.gob.pe/sprl/main/partidas-base-grafica-registral')
            # Esperar a que la nueva página cargue
            time.sleep(10)
            take_screenshot(driver, f"{pathpdf}/evidencias/partidas-base-grafica-registral.png")
            # Buscar el elemento app-select con el atributo formlabel="selectedOficinaRegistral"
            appSelectedOficinaRegistral = find_element_by(driver, By.CSS_SELECTOR, "app-select-oficina-registral[formlabel='selectedOficinaRegistral']", 5)

            # Buscar el select dentro de app-select
            selectOficinaRegistral = appSelectedOficinaRegistral.find_element(By.CLASS_NAME, "ant-select")
            # Hacer clic en el select para desplegar las opciones
            selectOficinaRegistral.click()
            # Buscar input dentro de appSelectedOficinaRegistral
            inputOficinaRegistral = appSelectedOficinaRegistral.find_element(By.CSS_SELECTOR, "input")
            # Simular escribir la variable oficina en el input
            inputOficinaRegistral.send_keys(oficina)
            # Dar enter para seleccionar  
            inputOficinaRegistral.send_keys(u'\ue007') 

            
            time.sleep(5)
            

            # Buscar el elemento app-select con el atributo formlabel="selectAreaRegistral"
            appSelectAreaRegistral = find_element_by(driver, By.CSS_SELECTOR, "app-select[formlabel='selectAreaRegistral']", 5)

            # Buscar el select dentro de app-select
            selectAreaRegistral = appSelectAreaRegistral.find_element(By.CLASS_NAME, "ant-select")

            # Hacer clic en el select para desplegar las opciones
            selectAreaRegistral.click()
            
            time.sleep(5)
            
            # Buscar todas las opciones desplegadas
            opcionesAreaRegistral = driver.find_elements(By.CSS_SELECTOR, ".ant-select-item-option")
            
            # Buscar la opción que contiene el texto "Propiedad Vehicular"
            for opcionar in opcionesAreaRegistral:
                if "Propiedad Vehicular" in opcionar.text:
                    opcionar.click()
                    break

            time.sleep(5)
            
            input_placa = find_element_by(driver, By.ID, 'numero',5)
            input_placa.send_keys(placa)

            # Buscar input con class img-captcha y guardar con screenshot_as_png
            img_captcha = find_element_by(driver, By.CLASS_NAME, 'img-captcha',5)
            captcha_png = img_captcha.screenshot_as_png
            captcha_image = Image.open(io.BytesIO(captcha_png))
            # Asegurar que el directorio existe
            path_captchas = f"{pathpdf}/evidencias/captchas"
            os.makedirs(path_captchas, exist_ok=True)
            # Guardar la imagen del captcha
            captcha_image.save(f"{path_captchas}/captcha_one.png", format="PNG")
            # Obtener el texto del captcha
            captcha_text1 = get_captcha(f"{path_captchas}/captcha_one.png") 
            
            captcha_text = captcha_text1
            # Ingresar el texto resuelto en el campo del captcha con id "codigoCaptcha"
            input_captcha = find_element_by(driver, By.ID, 'codigoCaptcha', 5)
            input_captcha.clear()
            for char in captcha_text:
                input_captcha.send_keys(char)
            
            # Buscar span con texto Buscar 
            span_buscar = find_element_by(driver, By.XPATH, "//span[contains(text(), 'Buscar')]", 5)
            # Obtener el button padre del span 
            button_buscar = span_buscar.find_element(By.XPATH, "..")
            # Hacer clic en el botón
            button_buscar.click()
            time.sleep(5)
            # obtener elemento con tag name nz-modal-confirm-container
            modal_confirm_offcaptcha = find_element_by(driver, By.TAG_NAME, 'nz-modal-confirm-container', 5)
            while modal_confirm_offcaptcha:
                # Obtener button con span y adentro text de Aceptar
                button_aceptar_offcaptcha = modal_confirm_offcaptcha.find_element(By.XPATH, ".//button[.//span[text()=' Aceptar ']]")
                # Hacer clic en el botón
                button_aceptar_offcaptcha.click()
                # Buscar input con class img-captcha y guardar con screenshot_as_png
                img_captcha = find_element_by(driver, By.CLASS_NAME, 'img-captcha',5)
                captcha_png = img_captcha.screenshot_as_png
                captcha_image = Image.open(io.BytesIO(captcha_png))
                # Asegurar que el directorio existe
                os.makedirs(path_captchas, exist_ok=True)
                # Guardar la imagen del captcha
                captcha_image.save(f"{path_captchas}/captcha_one.png", format="PNG")
                # Obtener el texto del captcha
                captcha_text1 = get_captcha(f"{path_captchas}/captcha_one.png") 
                
                captcha_text = captcha_text1
                # Ingresar el texto resuelto en el campo del captcha con id "codigoCaptcha"
                input_captcha = find_element_by(driver, By.ID, 'codigoCaptcha', 5)
                input_captcha.clear()
                for char in captcha_text:
                    input_captcha.send_keys(char)
                
                # Buscar span con texto Buscar 
                span_buscar = find_element_by(driver, By.XPATH, "//span[contains(text(), 'Buscar')]", 5)
                # Obtener el button padre del span 
                button_buscar = span_buscar.find_element(By.XPATH, "..")
                # Hacer clic en el botón
                button_buscar.click()
                time.sleep(5)
                # obtener elemento con tag name nz-modal-confirm-container
                modal_confirm_offcaptcha = find_element_by(driver, By.TAG_NAME, 'nz-modal-confirm-container', 5)
            # Esperar a que la tabla esté presente
            take_screenshot(driver, f"{pathpdf}/evidencias/resultado_asientos.png")

            # Esperar y obtener el contenedor con ID 'tabla'
            tabla_element = find_element_by(driver, By.ID, 'tabla', 5)

            # Buscar el primer botón dentro del contenedor
            button_tabla = tabla_element.find_element(By.TAG_NAME, 'button')

            # Hacer clic en el botón
            button_tabla.click()

            # Esperar para que la acción tenga efecto (evita usar sleep si puedes usar WebDriverWait)
            time.sleep(5)

            # Tomar screenshot después de la acción
            take_screenshot(driver, f"{pathpdf}/evidencias/tabla_asientos.png")
            
            # buscar Elemento con la class tablaLeyenda 
            tablaLeyenda = find_element_by(driver, By.CLASS_NAME, 'tablaLeyenda', 5)

            # Obtener los tr dentro del tbody de tablaLeyenda
            tbody = tablaLeyenda.find_element(By.TAG_NAME, 'tbody')
            filas = tbody.find_elements(By.TAG_NAME, 'tr')

            # Foreach de filas
            asientos_data = []  # Lista para almacenar todos los datos

            for fila in filas:
                # Buscar el div con el texto Titulo y obtener el texto completo 
                div_titulo = fila.find_element(By.XPATH, ".//div[contains(text(), 'Titulo')]")
                # Obtener el texto completo
                text_titulo = div_titulo.text
                # Obtener span del div_titulo y hacer click
                span_titulo = div_titulo.find_element(By.TAG_NAME, 'span')
                span_titulo.click()
                
                time.sleep(5)
                # Tomar screenshot después de la acción
                path_titulo = f"{pathpdf}/evidencias/{text_titulo}"
                os.makedirs(path_titulo, exist_ok=True)

                take_screenshot(driver, f"{path_titulo}/{text_titulo}.png")
                
                
                # obtener elemento con tag name nz-modal-confirm-container
                modal_confirm = find_element_by(driver, By.TAG_NAME, 'nz-modal-confirm-container', 5)
                # Obtener elemento con tag name table dentro de modal_confirm
                table = modal_confirm.find_element(By.TAG_NAME, 'table')
                rows = table.find_elements(By.TAG_NAME, 'tr')

                # Obtener el texto y limpiarlo
                text_titulo = div_titulo.text.replace("Titulo:", "").strip()

                # Separar por ' - ' para obtener año y número
                partes = text_titulo.split(" - ")
                # Obtener div  Nro. Asiento: 
                div_nro_asiento = fila.find_element(By.XPATH, ".//div[contains(text(), 'Nro. Asiento')]")
                # Obtener el texto completo
                text_nro_asiento = div_nro_asiento.text.replace("Nro. Asiento:", "").strip()
                
                
                # Guardar en el diccionario
                datos = {
                    "Año": partes[0].strip(),
                    "Titulo": partes[1].strip(),
                    "NroAsiento": text_nro_asiento
                }

                for row in rows:
                    cells = row.find_elements(By.TAG_NAME, 'td')
                    if len(cells) == 2:
                        key = cells[0].text.strip().replace(":", "")  # Limpiamos el texto del campo clave
                        value = cells[1].text.strip()
                        datos[key] = value

                asientos_data.append(datos)  # Agregar los datos de esta fila a la lista principal
                # Obtener button con span y adentro text de Aceptar
                button_aceptar = modal_confirm.find_element(By.XPATH, ".//button[.//span[text()=' Aceptar ']]")
                # Hacer clic en el botón
                button_aceptar.click()
                time.sleep(5)
                

            for asiento in asientos_data:
                # Obtener el año y el título
                anio = asiento["Año"]
                titulo = asiento["Titulo"]
                
                # Llamar a la función get_pdf_asiento
                message, path_pdf_asiento = get_pdf_asiento(oficina, anio, titulo, driver, path_titulo)

                # Agregar pdfs a asiento
                asiento["pdfs"] = path_pdf_asiento
            message = 'Asientos encontrados'
            return message, asientos_data
                        
            
    except Exception as e:
        print(f"Error: {e}")
        raise e
    
def get_pdf_asiento(oficina, anio, titulo, driver, pathpdf):
    

    # Simular Ctrl + T (nueva pestaña)
    actions = ActionChains(driver)
    actions.key_down(Keys .CONTROL).send_keys('t').key_up(Keys.CONTROL).perform()

    # Cambiar a nueva pestaña
    driver.switch_to.window(driver.window_handles[-1])


    driver.get('https://sigueloplus.sunarp.gob.pe/siguelo/')
    time.sleep(5)
    actions.send_keys(Keys.ESCAPE).perform()
    time.sleep(5)
    
    # Obtener  button con la class btn-sunarp-cyan
    button_acepto = find_element_by(driver, By.CLASS_NAME, 'btn-sunarp-cyan', 5)
    # validar si el boton fue encontrado si no se encuentra no hacer click
    if button_acepto:
        
        # Hacer clic en el botón
        button_acepto.click()
    take_screenshot(driver, f"{pathpdf}/open_page_siguelo.png")
    time.sleep(5)
    inyectar_interceptor_turnstile(driver)
    # Esperar a que algo dispare el render
    time.sleep(3) 
    ts_data = extraer_datos_turnstile(driver)
    token = resolver_turnstile_2captcha(ts_data, API_KEY)
    inyectar_token(driver, token)
    take_screenshot(driver, f"{pathpdf}/open_page_siguelo2.png")
    return
    turnstile_div = find_element_by(driver, By.CLASS_NAME, "cf-turnstile", 5)
    if turnstile_div:
        # imprimir div turnstile con contenido
        
        page_url = driver.current_url
        token = get_turnstile_token(page_url)
        # Ejecutar un script para establecer el token en el campo de entrada
        driver.execute_script("""
            document.querySelector('[name="cf-turnstile-response"]').value = arguments[0];
        """, token)
        time.sleep(5)
        take_screenshot(driver, f"{pathpdf}/open_page_siguelo2.png")

        # Obtener input type checkbox dentro de turnstile_div y hacer click
        checkbox_turnstile = turnstile_div.find_element(By.CSS_SELECTOR, "input[type='checkbox']")
        checkbox_turnstile.click()
        time.sleep(5)

    # Obtener select con id cboOficina
    select_oficina = find_element_by(driver, By.ID, 'cboOficina', 5)
    # Hacer clic en el select para desplegar las opciones
    select_oficina.click()
    time.sleep(5)
    # Buscar todas las opciones desplegadas
    opciones_oficina = select_oficina.find_elements(By.TAG_NAME, "option")
    # Buscar la opción que contiene el texto de la oficina
    for opcion in opciones_oficina:
        if oficina in opcion.text:
            opcion.click()
            break
    time.sleep(5)
    
    # Obtener select con id cboAnio
    select_anio = find_element_by(driver, By.ID, 'cboAnio', 5)
    # Hacer clic en el select para desplegar las opciones
    select_anio.click()
    time.sleep(5)
    # Buscar todas las opciones desplegadas
    opciones_anio = select_anio.find_elements(By.TAG_NAME, "option")
    # Buscar la opción que contiene el texto del año
    for opcion in opciones_anio:
        if anio in opcion.text:
            opcion.click()
            break
    time.sleep(5)
    
    # Obtener input name numeroTitulo
    input_numero_titulo = find_element_by(driver, By.NAME, 'numeroTitulo', 5)
    # Limpiar el campo de texto
    input_numero_titulo.clear()
    # Ingresar el texto del título
    input_numero_titulo.send_keys(titulo)
    time.sleep(5)
    # Obtener img canva con id textCanvas

    
    
    # Buscar button con texto BUSCAR
    button_buscar = find_element_by(driver, By.XPATH, "//button[contains(text(), 'BUSCAR')]", 5)
    # Hacer clic en el botón
    button_buscar.click()
    time.sleep(5)
    
    button_ok_off_captcha = find_element_by(driver, By.XPATH, "//button[contains(text(), 'OK')]", 5)
    while button_ok_off_captcha:
        
        # Hacer clic en el botón
        button_ok_off_captcha.click()
        time.sleep(5)
        turnstile_div = find_element_by(driver, By.CLASS_NAME, "cf-turnstile", 5)
        if turnstile_div:
            sitekey = turnstile_div.get_attribute("data-sitekey")
            page_url = driver.current_url
            token = get_turnstile_token(sitekey, page_url)
            # Ejecutar un script para establecer el token en el campo de entrada
            driver.execute_script("""
                document.querySelector('[name="cf-turnstile-response"]').value = arguments[0];
            """, token)
            time.sleep(5)
            # Obtener input type checkbox dentro de turnstile_div y hacer click
            checkbox_turnstile = turnstile_div.find_element(By.CSS_SELECTOR, "input[type='checkbox']")
            checkbox_turnstile.click()
            time.sleep(5)
        # Buscar button con texto BUSCAR
        button_buscar = find_element_by(driver, By.XPATH, "//button[contains(text(), 'BUSCAR')]", 5)
        # Hacer clic en el botón
        button_buscar.click()
        time.sleep(5)
        
        button_ok_off_captcha = find_element_by(driver, By.XPATH, "//button[contains(text(), 'OK')]", 5)
    
    take_screenshot(driver, f"{pathpdf}/resultado_siguelo_pdf.png")
    
    
    # Obtener a que contenga un span con un elemento mat-icon y el text " Acceder al asiento de inscripción y TIVE"
    button_descargar = find_element_by(driver, By.XPATH, "//a[contains(., 'Acceder al asiento de inscripción y TIVE')]", 5)
    if not button_descargar:
        pdfs = []
        message = 'No se pudieron descargar los PDFs'
        return message, pdfs
    # Imprimir el html button
    print(button_descargar.get_attribute('outerHTML')) 
    # Hacer scroll hasta el elemento del botón
    driver.execute_script("arguments[0].scrollIntoView();", button_descargar)
    # Tomar screenshot después de la acción
    # Hacer clic en el botón
    button_descargar.click()
    take_screenshot(driver, f"{pathpdf}/tabla_pdf_asientos.png")
    time.sleep(10)
    # Obtener elemento con class mat-card-content
    card_content = find_element_by(driver, By.CLASS_NAME, 'mat-card-content', 5)
    
    # Obtener tabla dentro de card content
    table = card_content.find_element(By.TAG_NAME, 'table')
    # Obtener los tbody
    tbody = table.find_element(By.TAG_NAME, 'tbody')
    # Obtener los tr dentro del tbody
    filas = tbody.find_elements(By.TAG_NAME, 'tr')
    pdfs = []
    for i, fila in enumerate(filas):
        # Si solo hay una fila, ejecutar solo esa
        if len(filas) == 1 and i == 0:
            pass
        # Si hay más de una fila, solo continuar con la primera y la última
        elif i != 0 and i != len(filas) - 1:
            continue

        # Obtener dentro del tr el button con class btn-success
        button_descargar = fila.find_element(By.CLASS_NAME, 'btn-success')
        button_descargar.click()
        time.sleep(10)

        path = f"{pathpdf}/*.pdf"
        if not glob.glob(path):
            path_pdf_titulo = None
        else:
            path_pdf_asiento = max(glob.iglob(path), key=os.path.getctime)
            nombre_pdf_asiento = os.path.basename(path_pdf_asiento)
            path_pdf_titulo = f"{pathpdf}/{titulo}/{i+1}/"
            os.makedirs(path_pdf_titulo, exist_ok=True)
            path_pdf_titulo = f"{pathpdf}/{titulo}/{i+1}/{nombre_pdf_asiento}"
            os.rename(path_pdf_asiento, path_pdf_titulo)

        pdfs.append(path_pdf_titulo)
    
    


        
        
    if pdfs:
        message = 'PDFs descargados exitosamente'
    else:
        message = 'No se pudieron descargar los PDFs'
    return message, pdfs



def inyectar_interceptor_turnstile(driver):
    js = """
    const i = setInterval(() => {
        if (window.turnstile) {
            clearInterval(i)
            window.turnstile.render = (a, b) => {
                const p = {
                    type: "TurnstileTaskProxyless",
                    websiteKey: b.sitekey,
                    websiteURL: window.location.href,
                    data: b.cData,
                    pagedata: b.chlPageData,
                    action: b.action,
                    userAgent: navigator.userAgent
                }
                console.log("###TS_DATA###" + JSON.stringify(p))
                window.tsCallback = b.callback
                return 'foo'
            }
        }
    }, 10)
    """
    driver.execute_script(js)   


def extraer_datos_turnstile(driver, timeout=10):
    print("⏳ Esperando los datos de Turnstile...")
    for _ in range(timeout * 10):
        logs = driver.get_log("browser")
        for entry in logs:
            if "###TS_DATA###" in entry["message"]:
                raw_json = entry["message"].split("###TS_DATA###")[1]
                print("✅ Datos capturados.")
                return json.loads(raw_json)
        time.sleep(0.5)
    raise Exception("❌ No se pudieron capturar los datos de Turnstile")

def inyectar_token(driver, token):
    print("🚀 Inyectando token en el navegador...")
    driver.execute_script(f'window.tsCallback("{token}")')
    print("✅ Token inyectado con éxito.")

def get_soats(placa, url, driver, idplacahistory, path):
    
    try:
        # Acceder a la URL
        driver.get(url)
        time.sleep(15)
        ventana_original = driver.current_window_handle
        
        path_evidencias = f"{path}/evidencias"
        os.makedirs(path_evidencias, exist_ok=True)
        take_screenshot(driver, f"{path_evidencias}/captura.png")
        # Buscar el elemento img
        captcha_img = find_element_by(driver, By.XPATH, "//img[@alt='captcha']", 5)

        captcha_png = captcha_img.screenshot_as_png
        captcha_image = Image.open(io.BytesIO(captcha_png))
        path_captchas = f"{path_evidencias}/captchas"
        os.makedirs(path_captchas, exist_ok=True)

        # Guardar la imagen del captcha
        captcha_image.save(f"{path_captchas}/captchasoat.png", format="PNG")
        captcha_text1 = get_captcha(f"{path_captchas}/captchasoat.png")
            
        captcha_text = captcha_text1
        # Ingresar el texto resuelto en el campo del captcha con id codigoCaptcha
        input_captcha = find_element_by(driver, By.NAME, 'captcha', 5)

        input_captcha.clear()
        for char in captcha_text:
            input_captcha.send_keys(char)
        time.sleep(5)
        take_screenshot(driver, f"{path_evidencias}/captcha_input.png")
        input_placa = find_element_by(driver, By.NAME, 'textfield', 5)
        for char in placa:
            input_placa.send_keys(char)
        time.sleep(5)
        take_screenshot(driver, f"{path_evidencias}/placa_input.png")

        btn_consultar = find_element_by(driver, By.ID, 'SOATForm', 5)
        btn_consultar.click()

        #Espera que aparezca una nueva ventana
        WebDriverWait(driver, 10).until(lambda d: len(d.window_handles) > 1)

        # Cambia el foco a la nueva ventana
        for handle in driver.window_handles:
            if handle != ventana_original:
                driver.switch_to.window(handle)
                break

        take_screenshot(driver, f"{path_evidencias}/consulta_nueva_ventana.png")

        # Capturamos los encabezados (ignorando el primero vacío)
        # Ignoramos el primer <td>
        header_elements = driver.find_elements(By.CSS_SELECTOR, "#grid1 thead tr td")[1:]  
        headers = [header.text.strip().split('\n')[0] for header in header_elements]

        # Capturamos las filas del cuerpo
        row_elements = driver.find_elements(By.CSS_SELECTOR, "#grid1 tbody tr")
        # construimos la lista soats 
        soats = []
        for row in row_elements:
            # Capturamos las celdas (ignoramos el primer td vacío)
            cell_elements = row.find_elements(By.TAG_NAME, "td")[1:]
            cells = [cell.text.strip() for cell in cell_elements]
            
            # Mapeamos encabezado -> valor
            row_data = dict(zip(headers, cells))
            soats.append(row_data)
        print(soats)
        message =  'soats obtenidos'
        
        return message, soats
    except Exception as e:

        return {"error": str(e)}, 500
    
    
    
def get_papeletas_callao(placa, idplacahistory, driver, url):
    # Acceder a la URL
    driver.get(url)
    time.sleep(15)
    take_screenshot(driver, 'callao.png')
    return True

def get_papeletas_lima(placa, idplacahistory, driver, url):
    # Acceder a la URL
    driver.get(url)
    time.sleep(15)
    take_screenshot(driver, 'lima.png')
    
    return True