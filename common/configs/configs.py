from common.utils.funciones import Path, os

#Definicion de directorios
BASE_DIR = Path.cwd().resolve()
TEMP_DIR = os.path.join(BASE_DIR, 'temp')
TEST_DIR = os.path.join(BASE_DIR, 'test')
LOGS_DIR = os.path.join(BASE_DIR, 'logs')
HTML_DIR = os.path.join(BASE_DIR, 'interfaz.html')
COMMON_COMMON_DIR = os.path.join(BASE_DIR, 'common')
COMMON_ASSETS_DIR = os.path.join(COMMON_COMMON_DIR, 'assets')
COMMON_STYLES_DIR = os.path.join(COMMON_ASSETS_DIR, 'styles')
COMMON_CSS_DIR = os.path.join(COMMON_STYLES_DIR, 'styles.css')
FEATURES_DIR =  os.path.join(BASE_DIR, 'features')