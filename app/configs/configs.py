from app.utils.funciones import Path, os
from app.utils.funciones import webdriver, Service, ChromeDriverManager

#Definicion de directorios
BASE_DIR = Path(Path.cwd().resolve())
TEMP_DIR = BASE_DIR/ 'temp'
TEST_DIR = BASE_DIR/ 'test'
LOGS_DIR = BASE_DIR/ 'logs'
HTML_DIR = BASE_DIR/ 'interfaz.html'
APP_DIR = BASE_DIR/ 'app'
CONFIGS_DIR = APP_DIR/ 'app'
CORE_DIR = APP_DIR/ 'core'
UTILS_DIR = APP_DIR/ 'utils'
ML_DIR = BASE_DIR/ 'ml'
DATA_DIR = ML_DIR/ 'data'
MODELS_DIR = ML_DIR/ 'models'

#Set para scrapping
site_url = 'https://zeus.sii.cl/cvc/stc/stc.html'
ml_path = MODELS_DIR/ '202407231124'
configs_path = ml_path/ 'config.yaml'

def call_driver():
    chrome_options = webdriver.ChromeOptions()
    # chrome_options.add_argument('headless')
    chrome_options.add_argument('--log-level=3')
    
    service = Service(ChromeDriverManager().install())
    return  webdriver.Chrome(service=service, options=chrome_options)