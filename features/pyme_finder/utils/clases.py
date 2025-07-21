from PySide6.QtCore import QThread, Signal
from features.pyme_finder.core.main import create_pyme_file
from common.configs.configs import TEMP_DIR

class SearchPyme(QThread):
    finished = Signal(str)
    
    def __init__(self, file_content:dict, values:dict):
        super().__init__()
        self.file_content = file_content
        self.temp_paths = {}
        self.values = values[0]
    
    def run(self):
        # scrape_rut_info()
        print(self.temp_paths)
        print(self.values)
        self.finished.emit(create_pyme_file(self.temp_paths, self.values))