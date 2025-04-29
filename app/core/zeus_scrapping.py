from pathlib import Path
import time
import cv2
from typing import Dict, List, Tuple, Union
import numpy as np
import pandas as pd
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.remote.webdriver import WebDriver

from app.configs.configs import (
    call_driver, site_url, ml_path, configs_path,
    TEST_DIR
)
from app.utils.funciones import (
    calcular_dv, extract_text, extract_number,
    get_cell_value, extract_rut_before_dash,
    get_textboxes, get_captcha_image, send_keys,
    handle_alert, extraer_informacion
)
from mltu.configs import BaseModelConfigs
from mltu.inferenceModel import OnnxInferenceModel
from mltu.utils.text_utils import ctc_decoder

class CaptchaModel(OnnxInferenceModel):
    """Modelo para predicción de CAPTCHAs."""
    
    def __init__(self, char_list: Union[str, list], *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.char_list = char_list
    
    def predict(self, image: np.ndarray) -> str:
        """Predice el texto del CAPTCHA desde una imagen."""
        image = cv2.resize(image, self.input_shapes[0][1:3][::-1])
        image_pred = np.expand_dims(image, axis=0).astype(np.float32)
        preds = self.model.run(self.output_names, {self.input_names[0]: image_pred})[0]
        return ctc_decoder(preds, self.char_list)[0]

class PymeDataFormatter:
    """Clase para el formateo de datos PYME desde archivos Excel."""
    
    def __init__(self, temp_path: Dict[str, Path], cell_addresses: Dict[str, str]):
        self.temp_path = temp_path
        self.cell_addresses = cell_addresses
        self.name_file, self.path_file = list(temp_path.items())[0]
    
    def _extract_excel_parameters(self) -> Tuple[str, str, int, int, str]:
        """Extrae los parámetros necesarios del Excel."""
        rut_column = extract_text(self.cell_addresses['rutPyme'])
        name_column = (extract_text(self.cell_addresses['namePyme']) 
                    if self.cell_addresses['namePyme'] else rut_column)
        first_row = extract_number(self.cell_addresses['rutPyme'])
        last_row = extract_number(self.cell_addresses['lastRowPyme'])
        sheet_name = self.cell_addresses['sheetname']
        return rut_column, name_column, first_row, last_row, sheet_name
    
    def format_data(self) -> Tuple[pd.DataFrame, str, str]:
        """Formatea los datos del archivo Excel."""
        rut_col, name_col, first_row, last_row, sheet_name = self._extract_excel_parameters()
        
        df = pd.read_excel(
            self.path_file,
            sheet_name=sheet_name,
            usecols=f'{rut_col}:{name_col}',
            skiprows=first_row-1,
            nrows=last_row
        )
        
        rut_value = get_cell_value(self.path_file, sheet_name, self.cell_addresses['rutPyme'])
        name_value = (get_cell_value(self.path_file, sheet_name, self.cell_addresses['namePyme'])
                    if self.cell_addresses['namePyme'] else False)
        
        return df, rut_value, name_value

class ZeusScraper:
    """Clase principal para el scraping de información PYME desde Zeus."""
    
    def __init__(self, temp_path: Dict[str, Path], cell_addresses: Dict[str, str]):
        self.temp_path = temp_path
        self.cell_addresses = cell_addresses
        self.driver = None
        self.model = self._initialize_model()
        self.ruts_pyme: List[Dict] = []
    
    def _initialize_model(self) -> CaptchaModel:
        """Inicializa el modelo de predicción de CAPTCHAs."""
        configs = BaseModelConfigs.load(configs_path)
        configs.model_path = ml_path
        return CaptchaModel(model_path=configs.model_path, char_list=configs.vocab)
    
    def _process_single_rut(self, rut: str) -> bool:
        """Procesa un único RUT y retorna True si fue exitoso."""
        rut = str(rut).replace('−','-').split('-')[0]
        dv = calcular_dv(rut)
        
        # Verificar si el RUT ya fue procesado
        if any(d['Rut']==f'{rut}-{dv}' for d in self.ruts_pyme):
            print(f'RUT {rut} ya procesado, saltando...')
            return True
        
        # Procesar el RUT
        textboxes = get_textboxes(self.driver)
        image = get_captcha_image(self.driver)
        captcha = self.model.predict(image)
        send_keys(textboxes, rut, dv, captcha)
        
        alert = handle_alert(self.driver)
        if alert == 'R':
            self.ruts_pyme.append({'Rut': rut,'Nombre Zeus': np.nan, 'Pyme': np.nan})
            self.driver.refresh()
            return True
        elif alert == 'C':
            self.driver.refresh()
            return False
        
        # Extraer información
        elements = WebDriverWait(self.driver, 10).until(
            EC.presence_of_all_elements_located((By.TAG_NAME, 'div'))
        )
        name, pyme = extraer_informacion(elements[0].text)
        self.ruts_pyme.append({'Rut': f'{rut}-{dv}', 'Nombre Zeus': name, 'Pyme': pyme})
        
        self.driver.get(site_url)
        return True
    
    def _format_results(self, df: pd.DataFrame, rut_col: str, name_col: str) -> pd.DataFrame:
        """Formatea los resultados finales en un DataFrame."""
        df_results = pd.DataFrame(self.ruts_pyme)
        df_results.sort_values(by='Rut', ascending=True, inplace=True)
        df_results.drop_duplicates(subset='Rut', inplace=True)
        df_results['Rut sin Dv'] = df_results['Rut'].apply(extract_rut_before_dash)
        
        if name_col:
            df['Rut sin Dv'] = df[rut_col].apply(extract_rut_before_dash)
            df_results = df_results.merge(df, on='Rut sin Dv', how='left')
            df_results.dropna(subset='Rut', inplace=True)
            df_results.drop_duplicates(subset='Rut', inplace=True)
            
            df_results[f'{name_col}Nuevo'] = np.where(
                df_results['Nombre Zeus'] != '**',
                df_results['Nombre Zeus'],
                df_results[name_col]
            )
            df_results = df_results[['Rut', 'Rut sin Dv', f'{name_col}Nuevo', 'Pyme']]
            df_results.rename({f'{name_col}Nuevo': name_col}, axis=1, inplace=True)
        
        return df_results[['Rut', 'Rut sin Dv', name_col, 'Pyme']]
    
    def scrape(self) -> str:
        """Ejecuta el proceso de scraping completo."""
        try:
            self.driver = call_driver()
            self.driver.get(site_url)
            
            # Preparar datos
            formatter = PymeDataFormatter(self.temp_path, self.cell_addresses)
            df, rut_col, name_col = formatter.format_data()
            ruts = df[rut_col].drop_duplicates().reset_index(drop=True)
            
            # Procesar RUTs
            start_time = time.time()
            total_ruts = len(ruts)
            
            print(f"\nIniciando procesamiento de {total_ruts} RUTs...")
            for i, rut in enumerate(ruts, 1):
                while not self._process_single_rut(rut):
                    continue
                # Mostrar progreso
                if i % 10 == 0 or i == total_ruts:
                    progress = (i / total_ruts) * 100
                    print(f"Progreso: {i}/{total_ruts} ({progress:.1f}%)")
            
            # Formatear y guardar resultados
            df_results = self._format_results(df, rut_col, name_col)
            output_path = Path(self.temp_path['fileInputPyme'])
            df_results.to_excel(output_path, sheet_name='Pyme', index=False)
            
            execution_time = time.time() - start_time
            print(f'\nProceso completado:')
            print(f'- Registros procesados: {total_ruts}')
            print(f'- Tiempo de ejecución: {execution_time:.2f} segundos')
            print(f'- Archivo guardado en: {output_path}')
            
            return 'Archivo Pyme creado exitosamente!'
            
        except Exception as e:
            return f'Error: {str(e)}'
        finally:
            if self.driver:
                self.driver.quit()

def create_pyme_file(temp_path: Dict[str, Path], cell_addresses: Dict[str, str]) -> str:
    """Función principal para crear el archivo PYME."""
    scraper = ZeusScraper(temp_path, cell_addresses)
    return scraper.scrape()

if __name__ == "__main__":
    # Ejemplo de uso
    test_temp_path = {
        'fileInputPyme': TEST_DIR / 'test_pyme.xlsx',
        'tempFile': TEST_DIR / 'temp_data.xlsx'
    }
    
    test_cell_addresses = {
        'rutPyme': 'A2',
        'namePyme': 'B2',
        'lastRowPyme': '10',
        'sheetname': 'Sheet1'
    }
    
    try:
        result = create_pyme_file(test_temp_path, test_cell_addresses)
        print(result)
    except Exception as e:
        print(f"Error en la ejecución: {e}")