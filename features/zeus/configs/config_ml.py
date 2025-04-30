from common.utils.funciones import Path, os
from common.configs.configs import FEATURES_DIR

#MACHINE LEARNING
ml_path = fr'{Path(FEATURES_DIR) }\pyme_finder\configs\ml\202407231124'
model_path = os.path.join(ml_path, 'model.h5')
configs_path = os.path.join(ml_path, 'configs.yaml')