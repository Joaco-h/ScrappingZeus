from app.utils.funciones import Path, os
from app.utils.funciones import webdriver, Service, ChromeDriverManager

#Definicion de directorios
BASE_DIR = Path.cwd().resolve()
TEMP_DIR = os.path.join(BASE_DIR, 'temp')
TEST_DIR = os.path.join(BASE_DIR, 'test')
LOGS_DIR = os.path.join(BASE_DIR, 'logs')
HTML_DIR = os.path.join(BASE_DIR, 'interfaz.html')
APP_DIR = os.path.join(BASE_DIR, 'app')
CONFIGS_DIR = os.path.join(APP_DIR, 'app')
CORE_DIR = os.path.join(APP_DIR, 'core')
UTILS_DIR = os.path.join(APP_DIR, 'utils')
ML_DIR = os.path.join(BASE_DIR, 'ml')
DATA_DIR = os.path.join(ML_DIR, 'data')
MODELS_DIR = os.path.join(ML_DIR, 'models')

#Set para scrapping
site_url = 'https://zeus.sii.cl/cvc/stc/stc.html'
ml_path = os.path.join(MODELS_DIR, '202407231124')
configs_path = os.path.join(ml_path, 'config.yaml')

def call_driver():
    chrome_options = webdriver.ChromeOptions()
    # chrome_options.add_argument('headless')
    chrome_options.add_argument('--log-level=3')
    
    service = Service(ChromeDriverManager().install())
    return  webdriver.Chrome(service=service, options=chrome_options)