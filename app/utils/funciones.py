import os
import io
import re
import sys
import cv2
import glob
import time
import typing
import shutil
import calendar
import openpyxl
import unidecode
import requests
import numpy as np
import pandas as pd
import xlwings as xw
from PIL import Image
from io import BytesIO
from pathlib import Path
from itertools import cycle
from functools import wraps
from datetime import datetime
from functools import partial
from PySide6.QtWidgets import QFileDialog
import win32com.client as win32
win32c = win32.constants

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

def handler_excel_errors(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except PermissionError as e:
            return f'Error de permisos: {e}'
        except FileNotFoundError as e:
            return f'Archivo no encontrado: {e}'
        except Exception as e:
            return f'Ocurrió un error inesperado: {e}'
    return wrapper

def extract_rut_before_dash(value):
    # Usar una expresión regular para encontrar la parte antes del guion
    match = re.match(r'^\s*([^-\s]+)', value)
    if match:
        return match.group(1)
    else:
        return None

def extract_number(s) -> list:
    """
    Extrae todos los números de una cadena.

    Args:
        s (str): La cadena de la que se extraerán los números.

    Returns:
        list: Una lista de números encontrados en la cadena. Si no se encuentra ningún número,
        devuelve una lista vacía.
    """
    pattern = r'\d+'
    result = re.findall(pattern, s)
    return int(result[0])

def extract_text(s) -> str:
    """
    Extrae todo el texto de una cadena, excluyendo los números.

    Args:
        s (str): La cadena de la que se extraerá el texto.

    Returns:
        str: El texto encontrado en la cadena, excluyendo los números. Si no se encuentra ningún texto,
        devuelve una cadena vacía.
    """
    pattern = r'[^\d]+'
    result = re.findall(pattern, s)
    return ''.join(result).strip()

def get_file_path(base_path, append_path) -> None:
    '''
    Esta función devuelve la ruta completa de un archivo dado su directorio y su nombre.

    Parámetros:
    base_path (str): El directorio donde se encuentra el archivo.
    append_path (str): El nombre del archivo.

    Retorna:
    str: La ruta completa del archivo.'''
    return os.path.join(base_path, append_path)

def validate_integer(func):
    @wraps(func)
    def wrapper(rut):
        try:
            int(rut)
            return func(rut)
        except ValueError:
            return rut
    return wrapper


def enter_captcha(driver, textboxes, rut, dv, captcha):
    textboxes['rut'].send_keys(rut)
    textboxes['dv'].send_keys(dv)
    textboxes['captcha'].send_keys(captcha)

    captcha_image_element = driver.find_element(By.ID, 'imgcapt')
    captcha_image_url = captcha_image_element.get_attribute('src')

    response = requests.get(captcha_image_url)
    captcha_image = Image.open(io.BytesIO(response.content))

    print(captcha_image)

    return captcha_image


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

def save_temp_file(dir, content):
    temp_paths = {}
    for name, file in content.items():
        temp_path = get_file_path(dir, f'{name}_temp.xlsx')
        temp_paths[name] = temp_path
        with open(temp_path, 'wb') as wb:
            wb.write(file.getbuffer())
    return temp_paths

def save_file_folder(save_type='file'):
    options = QFileDialog.Option()
    if save_type=='file':
        file_path, _ = QFileDialog.getSaveFileName(None, 'Guardar archivo Excel', '', 'Excel Files (*.xlsx);;All Files (*)', options=options)
    if save_type=='folder':
        file_path = QFileDialog.getExistingDirectory('Seleccionar carpetas', options=options)
    return file_path

def rename_temp_file(temp, real):
    if os.path.exists(real):
        os.remove(real)
    try:
        shutil.move(temp, real)
        return f'Archivo guardado en: {real}'
    except Exception as e:
        os.remove(temp)
        return f'Error al guardar el archivo: {e}'

def clean_folder(folder):
    files = glob.glob(folder+"/*")
    for file in files:
        try:
            os.remove(file)
            print(f'{file} eliminado')
        except:
            print(f'No se pudo eliminar el archivo {file}')

@validate_integer
def calcular_dv(rut):
    """
    Calculka el dígito verificador (DV) de un RUT en Chile.

    Args:
        rut (int): El número de RUT sin  el dígito verificador

    Returns:
        str: El dígito verificador
    """
    reversed_digits = map(int, reversed(str(rut)))
    factors = cycle(range(2, 8))
    s = sum(d * f for d, f in zip(reversed_digits, factors))
    dv = (-s) % 11
    return  str(dv) if dv != 10 else 'K'

def contains_keyword(keyword, value):
    """
    Verifica si el valor dado contiene la palabra clave especificada.
    
    Parámetros:
        value (str): La cadena en la que buscar.
        keyword (str): La palabra clave a buscar en la cadena.
    
    Returns:
        bool: Verdadero si la cadena contiene la palabra clave, Falso en caso contrario.
    """
    if isinstance(keyword, str) and isinstance(value, str):
        return unidecode.unidecode(keyword.lower()) in unidecode.unidecode(value.lower())
    return False

def get_cell_value(file_path, sheet_name, cell):
    workbook = openpyxl.load_workbook(file_path, sheet_name)
    sheet = workbook[sheet_name]
    
    value = sheet[cell].value
    
    return value