from utils.functions import Path, os

#Definicion de directorios
BASE_DIR = Path.cwd().resolve()
CONFIGS_DIR =  os.path.join(BASE_DIR, 'configs')
UTILS_DIR =  os.path.join(BASE_DIR, 'utils')
ML_DIR =  os.path.join(CONFIGS_DIR, 'ml')