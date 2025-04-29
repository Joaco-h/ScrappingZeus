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

def validate_integer(func):
    @wraps(func)
    def wrapper(rut):
        try:
            int(rut)
            return func(rut)
        except ValueError:
            return rut
    return wrapper

def email_decorator(func):
    def wrapper(*args, **kwargs):
        email_details = func(*args, **kwargs)
        send_email(**email_details)
    return wrapper

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

def get_file_path(base_path, append_path) -> None:
    '''
    Esta función devuelve la ruta completa de un archivo dado su directorio y su nombre.

    Parámetros:
    base_path (str): El directorio donde se encuentra el archivo.
    append_path (str): El nombre del archivo.

    Retorna:
    str: La ruta completa del archivo.'''
    return os.path.join(base_path, append_path)

def extract_columns(s) -> str:
    """
    Extrae las columnas de una cadena que sigue un patrón específico.
    El patrón busca cualquier texto que esté entre dos signos de dólar ($)

    Args:
        s (str): La cadena de la que se extraerán las columnas.

    Returns:
        str: La primera columna encontrada en la cadena. Si no se encuentra ninguna columna,
        devuelve None.
    """
    patter = r'\$(.*?)\$'
    result = re.findall(patter, s)
    return result[0] if result else None


def extract_row(s) -> str:
    """
    Extrae el número de fila de una cadena que sigue un patrón específico.
    El patrón busca cualquier número que esté entre dos signos de dólar ($) y que sea el
    último en la cadena.

    Args:
        s (str): La cadena de la que se extraerá el número de fila.

    Returns:
        str: El primer número de fila encontrado en la cadena. Si no se encuentra ningún número,
        de fila, devuelve None.
    """
    patter = r'\$(\d+)(?!.*\$)'
    result = re.findall(patter, s)
    return result[0] if result else None

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

def extract_rut_before_dash(value):
    # Usar una expresión regular para encontrar la parte antes del guion
    match = re.match(r'^\s*([^-\s]+)', value)
    if match:
        return match.group(1)
    else:
        return None

def auto_fit_column(path):
    """
    Ajusta automáticamente el ancho de las columnas en un archivo de Excel.

    Args:
        path (str): Ruta del archivo de Excel.
    """
    app = xw.App(visible=False)
    try:
        wb = xw.Book(path)

        for ws in wb.sheets:
            ws.autofit(axis="columns")

        wb.save(path)
    finally:
        app.quit()

def adjust_allignment_font(path, sheets_names):
    """
    Ajusta automáticamente la alineacion y la fuente de un archivo Excel

    Args:
        path (str): Ruta del archivo de Excel.
        sheet_names (list): Lista de nombres de las hojas en el archivo de Excel
        que se van a ajustar.

    Nota:
    Esta función ajusta la alineación a centrada y la fuente a Arial.
    """
    app = xw.App(visible=False)
    try:
        wb = xw.Book(path)

        for sheetname in sheets_names:
            ws = wb.sheets[sheetname]
            ws.used_range.api.HorizontalAlignment = xw.constants.HAlign.xlHAlignCenter
            ws.used_range.font.name = 'Arial'

        wb.save(path)
    finally:
        app.quit()

def remove_newlines(text):
    return text.replace('\n', '')

def ensure_directory_exists(path):
    if not os.path.exists(path):
        os.makedirs(path)

@email_decorator
def format_hes_email(path, subject, body, date, value):
    to_dict = {
        "Área Operaciones": {
            "to": "lvega@puertomejillones.cl",
            "cc": "dbattaglia@puertomejillones.cl; csolari@puertomejillones.cl; jsanmartins@puertomejillones.cl; fpapagallo@puertomejillones.cl"
        },
        "Área Sustentabilidad": {
            "to": "vchacon@puertomejillones.cl",
            "cc": "jrojas@puertomejillones.cl; jsanmartins@puertomejillones.cl; fpapagallo@puertomejillones.cl"
        },
        "Área SSO": {
            "to": "aalvarez@puertomejillones.cl",
            "cc": "jdelpozo@puertomejillones.cl; jsanmartins@puertomejillones.cl; fpapagallo@puertomejillones.cl"
        },
        "Área Personas": {
            "to": "cgundel@puertomejillones.cl",
            "cc": "mrojas@puertomejillones.cl; jsanmartins@puertomejillones.cl; fpapagallo@puertomejillones.cl"
        },
        "Área Comercial": {
            "to": "wrojasl@puertomejillones.cl",
            "cc": "jauad@puertomejillones.cl; jsanmartins@puertomejillones.cl; fpapagallo@puertomejillones.cl"
        },
        "Área Adm & Finanzas": {
            "to": "fpapagallo@puertomejillones.cl",
            "cc": "jsanmartins@puertomejillones.cl; kochoa@puertomejillones.cl"
        },
        "Área Informática": {
            "to": "ariverac@puertomejillones.cl",
            "cc": "jsanmartins@puertomejillones.cl; fpapagallo@puertomejillones.cl"
        },
    }

    to = to_dict.get(value, 'Área no valida').get("to")
    cc = to_dict.get(value, 'Área no valida').get("cc")
    attachments = get_file_path(path, "Control " + value + '.xlsx')
    subject = subject.format(
        datetime.now().strftime('%d-%m-%y'),
        value
    )
    body = body.format(last_day_date(date))
    return {
        "to": to,
        "cc": cc,
        "subject": subject,
        "body": body,
        "attachments": attachments,
    }

def send_email(to, cc, subject, body, attachments):
    outlook = win32.Dispatch('outlook.application')
    mail = outlook.CreateItem(0)

    mail.To = to
    mail.CC = cc
    mail.Subject = subject
    mail.Body = body
    mail.Attachments.Add(attachments)

    mail.Send()

def last_day_of_month(date):
    return calendar.monthrange(date.year, date.month)[1]

def last_day_date(date_str, format='%Y-%m'):
    date = datetime.strptime(date_str, format)
    lastday = last_day_of_month(date)
    date_lastday = datetime(date.year, date.month, lastday)
    return date_lastday.strftime('%d-%m-%y')

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