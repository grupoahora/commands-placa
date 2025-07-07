
from app.utils.chromedriver import get_driver, find_element_by, wait_for_page_load, take_screenshot
from selenium.webdriver.common.by import By
import time

def login_balance(user, password, driver):
    try:
        #sacar captura de pantalla
        
        # Iniciar sesión
        username_input = find_element_by(driver, By.NAME, "username")
        password_input = find_element_by(driver, By.NAME, "password")
        username_input.send_keys(user)
        password_input.send_keys(password)
        take_screenshot(driver, f"login.png")
        current_url = driver.current_url
        submit_button = find_element_by(driver, By.CLASS_NAME, 'btn')
        
        
        submit_button.click()
        
        # Esperar a que la nueva página cargue
        wait_for_page_load(driver, current_url)
        
        return True  # O cualquier valor que indique que el inicio de sesión fue exitoso
    except Exception as e:
        print(f"Error en login: {e}")
        raise e
    

def get_balance(driver):
    time.sleep(5)
    driver.execute_script("""
                let monto = document.querySelector('.monto');
                document.querySelector('body').prepend(monto);
        """)
    """Obtiene el saldo de la página después de iniciar sesión."""
    balance_element = find_element_by(driver, By.CLASS_NAME, 'monto')
    print(balance_element.text)
    return balance_element.text