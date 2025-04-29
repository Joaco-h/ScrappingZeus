from PySide6.QtCore import QThread, Signal
from common.utils.funciones import format_hes_email, save_temp_file
from features.pendiente_hes.utils.funciones import create_excel_file, split_excel_file
from common.configs.configs import TEMP_DIR

class ExcelWorker(QThread):
    finished = Signal(str)
    
    def __init__(self, file_content:dict):
        super().__init__()
        self.file_content = file_content
        self.temp_paths = {}
    
    def run(self):
        self.temp_paths = save_temp_file(TEMP_DIR, self.file_content)
        self.finished.emit(create_excel_file(self.temp_paths))

class SplitWorker(QThread):    
    def __init__(self, file_path, folder_path):
        super().__init__()
        self.file_path = file_path
        self.folder_path = folder_path
    
    def run(self):
        split_excel_file(self.file_path, self.folder_path)

class EmailWorker(QThread):
    def __init__(self, path, subject, body, date, values):
        super().__init__()
        self.path = path
        self.subject = subject
        self.body = body
        self.date = date
        self.values = values
        
    def run(self):
        
        for value in self.values:
            format_hes_email(self.path, self.subject, self.body, self.date, value)