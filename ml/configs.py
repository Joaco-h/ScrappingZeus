import os
from datetime import datetime
from mltu.configs import BaseModelConfigs
from app.utils.funciones import Path, os
from configs import FEATURES_DIR

#MACHINE LEARNING
ml_path = fr'{Path(FEATURES_DIR) }\pyme_finder\configs\ml\202407231124'
model_path = os.path.join(ml_path, 'model.h5')
configs_path = os.path.join(ml_path, 'configs.yaml')

class ModelConfigs(BaseModelConfigs):
    def __init__(self):
        super().__init__()
        self.model_path = os.path.join("models", datetime.strftime(datetime.now(), "%Y%m%d%H%M"))
        self.vocab = ""
        self.height = 50
        self.width = 200
        self.max_text_length = 0
        self.batch_size = 64
        self.learning_rate = 1e-3
        self.train_epochs = 1000
        self.train_workers = 20