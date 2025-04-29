from PySide6.QtCore import QThread, Signal
from features.pyme_finder.core.main import create_pyme_file
from common.utils.funciones import save_temp_file
from common.configs.configs import TEMP_DIR
import pandas as pd
class SearchPyme(QThread):
    finished = Signal(str)
    
    def __init__(self, file_content:dict, values:dict):
        super().__init__()
        self.file_content = file_content
        self.temp_paths = {}
        self.values = values[0]
    
    def run(self):
        # scrape_rut_info()
        self.temp_paths = save_temp_file(TEMP_DIR, self.file_content)
        print(self.temp_paths)
        print(self.values)
        self.finished.emit(create_pyme_file(self.temp_paths, self.values))