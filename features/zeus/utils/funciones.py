from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.edge.service import Service
from selenium.common.exceptions import TimeoutException, NoSuchElementException, NoAlertPresentException
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from mltu.configs import BaseModelConfigs
from mltu.inferenceModel import OnnxInferenceModel
from mltu.utils.text_utils import ctc_decoder, get_cer

from common.utils.funciones import re, np, cv2, Image, BytesIO, contains_keyword

def get_textboxes(driver):
    """
    Identifica todas los cuadros de texto en una página web y los devuelve
    en un diccionario.
    
    Parámetros:
        driver (objeto webdriver): La instancia de webdriver para interactuar con
        la página web.
    
    Devuelve:
        dict: Un diccionario que contiene los cuadros de texto 'rut'. 'dv' y 'captcha'.
    """
    input_elements = driver.find_elements(By.TAG_NAME, 'input')
    text_boxes = [elem for elem in input_elements if
                elem.get_attribute('type')=='text']
    return {'rut':text_boxes[0],
            'dv':text_boxes[1],
            'captcha':text_boxes[2]}


def get_captcha_image(driver):
    """
    Obtiene la imagen del captcha de una página web y la guarda como 'captcha.png'.
    
    Parámetros:
        driver (objeto webdriver): El controlador del navegador web.
    """
    
    captcha_element = driver.find_element(By.ID, 'imgcapt')
    
    png = captcha_element.screenshot_as_png
    im = Image.open(BytesIO(png))
    numpy_image = np.array(im)
    image = cv2.cvtColor(numpy_image, cv2.COLOR_RGB2BGR)
    return image

def send_keys(textboxes, rut, dv, captcha):
    """
    Sends the specified values to the given textboxes and presses Enter.
    
    Args:
        textboxes (dict): A dictionary mapping textbox names to their Selenium WD elements.
        rut (str): The RUT value to enter.
        dv (str): The DV value to enter.
        captcha (str): The CAPTCHA value to enter.
    """
    textboxes['rut'].clear()
    textboxes['rut'].send_keys(rut)
    textboxes['dv'].clear()
    textboxes['dv'].send_keys(dv)
    textboxes['captcha'].send_keys(captcha)
    textboxes['captcha'].send_keys(Keys.RETURN)

def handle_alert(driver):
    """
    Handle alerts that may appear during WebDriver interactions.
    
    Args:
        driver (webdriver.WebDriver): The WebDriver instance.
    
    Returns:
        str: A code indicating the type of alert encountered:
            - R: Rut alert
            - C: Verification code alert
            - N: No alert present
    """
    try:
        alert = driver.switch_to.alert
        alert_text = alert.text
        alert.accept()
        print(f'Texto de alerta: {alert_text}')
        if contains_keyword('rut', alert_text): return 'R'
        if contains_keyword('codigo de verificacion', alert_text): return 'C'
    except NoAlertPresentException:
        print('No se encontró ninguna alerta.')
        return 'N'

def extraer_informacion(texto):
    """
    Extrae el nombre o razón social y la información de si es una PYME o no de un texto dado.
    
    Parámetros:
        texto (str): El texto del que se extraerá la información.
    
    Devuelve:
        name (str): El nombre extraído del texto. Si no se encuentra, devuelve 'No encontrado'.
        is_pyme(str): La información de si es una PYME o no extraída  del texto. Si no se encuentra
        devuelve 'No encontrado'.
    """
    # Buscar el nombre o razón social
    name = re.search(r'Nombre o Razón Social :\s*(.*)\s*RUT Contribuyente', texto)
    name = name.group(1) if name else 'No encontrado'
    # Buscar la información de si es una PYME o no
    is_pyme = re.search(r'Contribuyente es Empresa de Menor Tamaño \(según Ley N°20.416\) \*:\s*(.*)\s*\(', texto)
    is_pyme = is_pyme.group(1) if is_pyme else 'No encontrado'
    
    return name, is_pyme