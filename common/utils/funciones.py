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
import numpy as np
from PIL import Image
from io import BytesIO
from pathlib import Path
from itertools import cycle
from functools import wraps
from datetime import datetime
from functools import partial
from PySide6.QtWidgets import QFileDialog

def validate_integer(func):
    @wraps(func)
    def wrapper(rut):
        try:
            int(rut)
            return func(rut)
        except ValueError:
            return rut
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

def extract_rut_before_dash(value):
    # Usar una expresión regular para encontrar la parte antes del guion
    match = re.match(r'^\s*([^-\s]+)', value)
    if match:
        return match.group(1)
    else:
        return None

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
