from utils.functions import Path, os
from configs.settings import ML_DIR

#MACHINE LEARNING
# ml_path = fr'{Path(ML_DIR) }\202407231124'
ml_path = os.path.join(ML_DIR, '202407231124')
model_path = os.path.join(ml_path, 'model.h5')
configs_path = os.path.join(ml_path, 'configs.yaml')