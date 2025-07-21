from PySide6.QtCore import QThread, Signal
from features.pyme_finder.core.main import create_pyme_file
from common.configs.configs import TEMP_DIR

class SearchPyme(QThread):
    finished = Signal(list)
    
    def __init__(self):
        super().__init__()
    
    def run(self):
        self.finished.emit(create_pyme_file())