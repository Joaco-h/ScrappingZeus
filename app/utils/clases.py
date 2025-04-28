from PySide6.QtCore import QThread, Signal
# from app.core.web_scrapping import create_pyme_file
from app.utils.funciones import save_temp_file, pd
from app.configs.configs import TEMP_DIR

class SalirBucle(Exception):
    pass

# class SearchPyme(QThread):
#     finished = Signal(str)
    
#     def __init__(self, file_content:dict, values:dict):
#         super().__init__()
#         self.file_content = file_content
#         self.temp_paths = {}
#         self.values = values[0]
    
#     def run(self):
#         # scrape_rut_info()
#         self.temp_paths = save_temp_file(TEMP_DIR, self.file_content)
#         print(self.temp_paths)
#         print(self.values)
#         self.finished.emit(create_pyme_file(self.temp_paths, self.values))