import os
import time
import cv2
import typing
import numpy as np
from pathlib import Path
from PIL import Image
from io import BytesIO
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