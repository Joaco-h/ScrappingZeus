import re
import os
import sys
import cv2
import time
import typing
import unidecode
import subprocess
import win32com.client

import numpy as np
import pandas as pd

from PIL import Image
from io import BytesIO
from functools import wraps
from itertools  import cycle
from datetime import datetime

from mltu.configs import BaseModelConfigs
from mltu.inferenceModel import OnnxInferenceModel
from mltu.utils.text_utils import ctc_decoder, get_cer

import xlwings as xw
from xlwings.constants import AutoFillType

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.edge.options import Options
from selenium.webdriver.edge.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException,
    WebDriverException,
    NoSuchElementException,
    NoAlertPresentException,
    InvalidSelectorException,
    StaleElementReferenceException,
    ElementNotInteractableException,
)
from webdriver_manager.microsoft import EdgeChromiumDriverManager
from selenium import webdriver

options = webdriver.EdgeOptions()
options.add_argument('start-maximized')
edge_options = webdriver.EdgeOptions()
edge_options.use_chromium = True
# edge_options.add_argument('headless')
# edge_options.add_argument('--log-level=3')


class SalirBucle(Exception):
    pass

class ImageToWordModel(OnnxInferenceModel):
    def __init__(self, char_list: typing.Union[str, list], *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.char_list = char_list

    def predict(self, image: np.ndarray):
        image = cv2.resize(image, self.input_shapes[0][1:3][::-1])

        image_pred = np.expand_dims(image, axis=0).astype(np.float32)

        preds = self.model.run(self.output_names, {self.input_names[0]: image_pred})[0]

        text = ctc_decoder(preds, self.char_list)[0]

        return text

class ExcelModifier():
    def __init__(self, columns):
        self.wb = None
        self.ws = None
        self.df = None
        self.app = None
        self.file = None
        self.df_kz = None
        self.df_db = None
        self.show_file = False
        self.sheet_name_db = None
        self.columns = columns
        self.columns_ws1 = list(self.columns.keys())
        self.columns_ws2 = list(self.columns.values())
        self.sheet_position = {}
        self.address_formula = {}
        self.columns_address = {}
        self.columns_position = {}
        self.columns_db = []
        self.wb_previous = None
        self.df_previous = None
        self.file_previous = None

    def get_df_kz(self):
        df_kz = self.df[self.df[self.columns_ws1[2]] == 'KZ']
        df_kz = df_kz.rename({self.columns_ws1[7]: self.columns_ws1[7] + '2'}, axis = 1)
        self.df_kz = df_kz

    def get_df_clean(self):
        df = self.df.merge(self.df_kz[[self.columns_ws1[-3], self.columns_ws1[7]+'2']],
                           on = self.columns_ws1[-3], how = 'left')
        df = df.dropna(subset = self.columns_ws1[7] + '2')
        self.df = df

    def get_df_db(self):
        df_db = self.df[self.df[self.columns_ws1[2]] != 'KZ']
        df_db = df_db.drop(self.columns_ws1[7], axis = 1)
        df_db = df_db.rename({self.columns_ws1[7] + '2': self.columns_ws1[7]}, axis = 1)
        df_db = df_db.rename(self.columns, axis = 1)
        self.df_db = df_db

    def move_sheets(self, new_name):
        try:
            self.app = xw.App(visible=self.show_file)
            target_file = xw.Book()
            self.wb_previous = self.app.books.open(self.file_previous)

            wb_sap = self.app.books.open(self.file)
            sheet_sap = wb_sap.sheets['Sheet1']
            sheet_sap.copy(before = target_file.sheets[0], name = new_name)

            for sheetname, pos in self.sheet_position.items():
                sheet = self.wb_previous.sheets[sheetname]
                sheet.copy(before = target_file.sheets[pos])

            wb_sap.close()
            target_file.save(self.file)
        finally:
            self.app.quit()

    def update_references_on_cells(self):
        try:
            self.app = xw.App(visible=self.show_file)
            self.wb = self.app.books.open(self.file)
            path_bracket = path_format_with_bracket(self.file)
            path_bracket_previous = path_format_with_bracket(self.file_previous)
            for sheet in self.wb.sheets:
                ws = self.wb.sheets[sheet]
                ws.used_range.api.Replace(self.file_previous, self.file)
                ws.used_range.api.Replace(path_bracket_previous, path_bracket)
                self.wb.save(self.file)
        finally:
            self.app.quit()

    def retrivieng_all_coordinates(self, columns_list : list) -> None:
        """
        Obtiene todas las coordenadas de las columnas objetivo.

        Args:
            columns_list (list): Una lista con todos los diccionario que utiliza
            para encontrar las columnas donde se encuentran las columnas obj.
        """
        try:
            self.app = xw.App(visible=self.show_file)
            self.wb = self.app.books.open(self.file)
            for cell in self.ws.range('2:2'):
                if cell.value in columns_list:
                    self.columns_address[cell.value] = cell.address
            self.wb.save(self.file)
        finally:
            self.app.quit()

    def write_df_on_file(self, month, year):
        try:
            self.app = xw.App(visible=self.show_file)
            self.wb = self.app.books.open(self.file)

            self.wb.sheets.add(f'{month} {year}', before = 3)
            self.wb.sheets.add(f'KZ {month} {year}', before = 4)

            df_sheet = self.wb.sheets(f'{month} {year}')
            df_sheet_kz = self.wb.sheets(f'KZ {month} {year}')

            df_sheet['A1'].options(pd.DataFrame,
                                index = False, header = True, expand='table').value = self.df
            df_sheet_kz['A1'].options(pd.DataFrame,
                                index = False, header = True, expand='table').value = self.df_kz

            self.wb.save(self.file)

        finally:
            self.app.quit()

    def write_formula_on_file(self):
        """
        Genera las formulas que deben ir en el archivo de excel.
        En los If 
        Si entra en 1 la formula solo se escribe en la primera fila
        Si entra en 3 la formula solo se escribe en la tercera fila
        Por ultimo si entre en else statement se escribe en la fila 3 y en la fila 1, 
        en la fila 1 se rescribe el rango al que lee al formula para que considere todos los valores.
        """
        columns_positionformula = {
            'Tipo Doc':3, '# P-E':3, '# P-E/R':0, 'Plazo':3, 'Monto':1, 'Moneda':1, 'Texto':1,
            'Nombre Proveedor':3, 'Pyme':3
        }
        try:
            app = xw.App(visible=self.show_file)
            wb = app.books.open(self.file)
            ws = wb.sheets[self.sheet_name_db]
            retrivieng_columns = list(columns_positionformula.keys())
            start_address, end_address = extract_address_from_range(ws.used_range.address)
            self.start_row, self.end_row = extract_row(start_address), extract_row(end_address)
            self.start_col,self.end_col = extract_columns(start_address),extract_columns(end_address)

            for cell in ws.range(f'{self.start_col}2:{self.end_col}2'):
                if cell.value in retrivieng_columns:
                    self.columns_position[cell.value] = extract_columns(cell.address)

            for key, value in columns_positionformula.items():
                if value == 1:
                    self.address_formula[
                        self.columns_position[key] + '1'] = ws.range(
                            self.columns_position[key] + '1').formula
                elif value == 3:
                    self.address_formula[
                        self.columns_position[key] + '3'] = ws.range(
                            self.columns_position[key] + '3').formula
                else:
                    self.address_formula[
                        self.columns_position[key] + '1'] = ws.range(
                            self.columns_position[key] + '1').formula
                    self.address_formula[
                        self.columns_position[key] + '3'] = ws.range(
                            self.columns_position[key] + '3').formula
            wb.save(self.file)
        finally:
            app.quit()

    def clean_old_data(self):
        try:
            app = xw.App(visible=self.show_file)
            wb = app.books.open(self.file)
            ws = wb.sheets[self.sheet_name_db]

            start_row_values = str(int(self.start_row) + 2)
            ws.range(f'{self.start_col}{self.start_row}:'
                    f'{self.end_col}{self.start_row}').clear_contents()
            ws.range(f'{self.start_col}{start_row_values}:'
                    f'{self.end_col}{self.end_row}').clear_contents()
            wb.save(self.file)
        finally:
            app.quit()

    def update_formulas_to_new_period(self):
        path_bracket = path_format_with_bracket(self.file[3:])
        path_bracket_previous = path_format_with_bracket(self.file_previous[3:])
        
        for address, formula in self.address_formula.items():
            new_formula = formula.replace(
                self.file_previous[3:], self.file[3:])
            new_formula = new_formula.replace(
                path_bracket_previous, path_bracket)
            self.address_formula[address] = new_formula

    def write_new_data_file(self, row_number):
        try:
            app = xw.App(visible=self.show_file)
            wb = app.books.open(self.file)
            ws = wb.sheets(self.sheet_name_db)

            ws['A3'].options(pd.DataFrame,
                                index = False, header = False, expand='table').value = self.df_db

            for address, formula in self.address_formula.items():
                if 'SUBTOTAL' in formula:
                    ws.range(address).value = change_last_value(formula, row_number + 2)
                else:
                    ws.range(address).value = formula
                if '3' in address:
                    address_column = extract_letters_numbers(address)[0]
                    ws.range(address).api.AutoFill(
                        ws.range(f'{address}:{address_column}{row_number + 2}'
                                    ).api, AutoFillType.xlFillDefault)
            wb.save(self.file)
        finally:
            app.quit()

class DatesFormat():
    """
    Clase que maneja los formatos de fechas.
    """
    def __init__(self, month, year):
        self.month = get_month(month)
        self.month_on_year = range(1,13)
        self.month_two_digits = format_two_digits(month)
        self.long_year, self.short_year = get_year(year)
        self.update_date = datetime(int(self.long_year), int(self.month), 1, 0, 0)
        self.period = self.month_two_digits + '-' + self.long_year
        self.period_previous = get_previous_period(self.period)
        self.month_previous, self.year_previous = self.period_previous.split('-')

def check_numeric_value(number_digits):
    """
    Este es un decorador que verifica si el primer argumento de una función es
    un número entero con una cantidad específica de dígitos. Si no es así, se
    lanza un ValueError.

    Args:
        number_digits (int): La cantidad de dígitos que se espera que tenga
        el número
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            value = args[0]
            is_numeric = str(value).isdigit()
            len_number = len(str(value))
            if  not is_numeric or len_number != number_digits:
                raise ValueError(f'El valor {value} no es un '
                                 f'número entero de la longitud correcta({number_digits})')
            return func(*args, **kwargs)
        return wrapper
    return decorator

def check_valid_month(func):
    """
    Verifica si el primer argumento de una función es un número entero válido para un 
    mes (entre 1 y 12), si no es así, retorn ValueError

    Args:
        func (function): La función que se aplicará al argumento si es un mes valido.
    """
    def wrapper(*args, **kwargs):
        month = args[0]
        is_numeric = str(month).isdigit()
        valid_month = int(month) not in [num for num in range(1,13)]
        if not is_numeric or valid_month:
            raise ValueError('El valor ingresado no es un número entero entre 1 y 12')
        return func(*args, **kwargs)
    return wrapper


def validar_entrada(func):
    def wrapper(rut):
        if not rut or rut=='':
            print('El valor recibido está vacío.')
            return 0
        return func(rut)
    return wrapper

def validate_integer(func):
    @wraps(func)
    def wrapper(rut):
        try:
            int(rut)
            return func(rut)
        except ValueError:
            return rut
    return wrapper

@validar_entrada
def limpiar_rut(rut):
    rut = str(rut)
    if '-' in rut:
        rut = rut.split('-')[0]
    return int(rut.replace('.',''))

def get_file_path(base_path, append_path) -> None:
    '''
    Esta función devuelve la ruta completa de un archivo dado su directorio y su nombre.

    Parámetros:
    base_path (str): El directorio donde se encuentra el archivo.
    append_path (str): El nombre del archivo.

    Retorna:
    str: La ruta completa del archivo.'''
    return os.path.join(base_path, append_path)

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

def get_class(df):
    non_ab = df[(df['Clase']!='AB') & (df['Clase']!='') & (df['Clase'].notna())]
    
    if  len(non_ab) > 0:
        return non_ab.iloc[0]['Clase']
    return 'AB'

def convert_float(num):
    return float(str(num).replace('.','').replace(',','.'))

def convert_float_sap(num):
    if '-' in num:
        return -float(str(num).replace('.','').replace(',','.').replace('-',''))
    return convert_float(num)

def path_format_with_bracket(path):
    """
    Esta función agrega corchetes al nombre del archivo en una ruta dada.

    Args:
        path (str): La ruta del archivo a la que se agregarán corchetes.

    Returns:
        nueva_ruta: La ruta del archivo con corchetes agregados al nomrbre
        del archivo.
    """
    # Separar la ruta en directorios y nombre de archivo
    directorios = path.split("\\")
    archivo = directorios[-1]

    # Agregar corchetes al nombre del archivo
    archivo_con_corchetes = "[" + archivo + "]"

    # Reemplazar el nombre del archivo en la ruta
    nueva_ruta = path.replace(archivo, archivo_con_corchetes)

    return nueva_ruta


def extract_address_from_range(range_string):
    """
    Extrae los nombres de las columnas de una cadena de rango en una hoja de cálculo.

    Parámetros:
        range_string (str): La cadena de rango de la que se extraerán los nombres de las columnas.
        Debe estar en el formato 'Hoja1!A1:B2' o 'A1:A2'
    Devuelve:
        (strat_col, end_col) (tuple): Una tupla que contiene los nombres de las columnas de inicio
        y fin extraídos de la cadena de rango.
    """
    # Extract the column names from the range string
    start_col, end_col = range_string.split(" ")[-1].split(":")
    return (start_col, end_col)

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


def change_last_value(formula, nuevo_valor):
    """
    Reemplza el último valor numérico en una fórmula dada con un nuevo valor.

    Parámetros:
        formula (str): La fórmula original que puede contener valores númericos.
        nuevo_valor (int/float): El nuevo valor que reemplazará al último valor
        númerico en la fórmula.

    Devuelve:
        nueva_formula (str):La fórmula con el último valor númerico reemplazado por el neuvo valor.
        Si no hay números en la fórmula, se devuelve la fórmula original.
    """
    # Encuentra todos los valores numéricos en la fórmula
    numeros = re.findall(r'\d+', formula)
    # Si no hay números en la fórmula, devolvemos la fórmula original
    if not numeros:
        return formula
    # Obtenemos el último número en la fórmula
    ultimo_numero = numeros[-1]
    # Reemplazamos el último número con el nuevo valor
    nueva_formula = formula[::-1].replace(ultimo_numero[::-1], str(nuevo_valor)[::-1], 1)[::-1]
    return nueva_formula

def extract_letters_numbers(cadena):
    """
        Esta función extrae todas las letras y números de una cadena dada.

    Parámetros:
    cadena (str): La cadena de la cual extraer las letras y números.

    Devuelve:
    letras (str): Todas las letras extraídas de la cadena.
    numeros (str): Todos los números extraídos de la cadena
    """
    letras = ''.join(re.findall('[a-zA-Z]', cadena))
    numeros = ''.join(re.findall('[0-9]', cadena))
    return letras, numeros

def format_two_digits(n):
    """
    Esta función toma un número entero y devuelve una cadena de caracteres que representa el mes,
    asegurándose de que siempre tenga dos dígitos. Por ejemplo, convierte el número 1 en la cadena '01'.

    Args:
        n (int): Un número entero que representa el mes.

    Returns:
        str: Una cadena de caracteres que representa el mes con dos dígitos.
    """
    return f'{int(n):02d}'

@check_valid_month
def get_month(month) -> str:
    """
    Esta función toma un mes como entrada y devuelve el mes como una cadena.
    La función está decorada con el decorador 'check_valid_month' que verifica si el mes es
    un número entero válido entre 1 y 12.

    Args:
        month (int): El mes a procesar.

    Returns:
        str: El mes como una cadena.
    """
    month = str(int(float(month)))
    return month

@check_numeric_value(4)
def get_year(year) -> str:
    """
    Esta función toma un año como entrada y devuelve una lista que contiene el año completo
    y los últimos dos digitos del año.
    La funcion esta decorada con el decorador 'check_numeric_value' que verifica si el año es
    un número de 4 dígitos.

    Args:
        year (int): El año a procesar

    Returns:
        list: Una lista que contiene el año completo y los últimos dos dígitos del año.
    """
    year = str(int(float(year)))
    return [year,year[-2:]]

def get_previous_period(period):
    """
    Retorna el period anterior dado un periodo en el formato 'mm-yyyy'

    Args:
        period (str): El periodo actual en el formato 'mm-yyyy'
    Returns:
    str: El periodo anterior en el mismo formato
    """
    month, year = map(int, period.split('-'))
    if month == 1:
        previous_month = 12
        previous_year = year - 1
    else:
        previous_month = month - 1
        previous_year = year

    previous_period = f'{previous_month:02d}-{previous_year}'
    return previous_period

def extract_month_year_from_file_path(file_path):
    """
    Extrae el mes y año de un archivo Excel en la ruta dada.

    Args:
        file_path (str): Ruta completa del archivo.
        
    Returns:
    str: El mes y año en formato 'mm-yyyy'
    """
    file_name = file_path.split('\\')[-1]
    index = file_name.find('CxP ')
    month_year = file_name[index + 7:index + 14]
    return month_year

def month_spanish(month):
    """
    Devuelve el nombre escrito del mes dado su valor númerico.

    Args:
        month (str): El mes en su representacion númerica.

    Returns:
        str: Nombre escrito del mes.
    """
    dict_month_spanish = {
        '1':'Enero',
        '2':'Febrero',
        '3':'Marzo',
        '4':'Abril',
        '5':'Mayo',
        '6':'Junio',
        '7':'Julio',
        '8':'Agosto',
        '9':'Septiembre',
        '10':'Octubre',
        '11':'Noviembre',
        '12':'Diciembre',
    }
    return dict_month_spanish[month]

def contains_keyword(keyword, value):
    """
    Verifica si el valor dado contiene la palabra clave especificada.

    Parámetros:
        value (str): La cadena en la que buscar.
        keyword (str): La palabra clave a buscar en la cadena.

    Returns:
        bool: Verdadero si la cadena contiene la palabra clave, Falso en caso contrario.
    """
    if isinstance(value, str):
        return unidecode.unidecode(keyword) in unidecode.unidecode(value.lower())
    return False


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

def setup_driver(driver_path):
    edge_options = Options()
    edge_options.add_argument('--log-level=3')

    service = Service(executable_path=driver_path)
    driver_edge = webdriver.Edge(service=service, options=edge_options)
    return driver_edge

def send_keys(textboxes, rut, dv, captcha):
    textboxes['rut'].clear()
    textboxes['rut'].send_keys(rut)
    textboxes['dv'].clear()
    textboxes['dv'].send_keys(dv)
    textboxes['captcha'].send_keys(captcha)
    textboxes['captcha'].send_keys(Keys.RETURN)

def handle_alert(driver):
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
    