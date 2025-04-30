from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWebEngineCore import QWebEnginePage
from PySide6.QtWidgets import QApplication, QMainWindow
from PySide6.QtCore import QUrl, QFileSystemWatcher, Slot, QObject
from PySide6.QtWebChannel import QWebChannel

from app.configs.configs import TEMP_DIR, HTML_DIR
from app.utils.funciones import io, sys
from app.utils.funciones import Path, get_file_path, clean_folder, rename_temp_file, save_file_folder

class CustomWebPage(QWebEnginePage):
    """Clase personalizada para capturar console.log de JavaScript y mostrarlo en la terminal de Python."""
    def javaScriptConsoleMessage(self, level, message, line, sourceID):
        print("JS Console")
        print("Mensaje desde Consola:")
        print(f"{message}")
        print("Detalles:")
        print(f"(Line {line}) in {sourceID}")
        print("------------------------------------------------------------------------------------")


class CallHandler(QObject):
    def __init__(self):
        super().__init__()
        self.uploaded_files = {}
    
    #Botones del Sidebar
    @Slot()
    def close_application(self):
        clean_folder(TEMP_DIR, '*') #Limpiar la carpeta temp cada vez que se inicia la app
        print("Cerrando aplicacion...")
        QApplication.instance().quit()
    
    @Slot(str, str, list, result=str)
    def send_file_to_backend(self, filename, idfile, file_content):
        print(f"send_file_to_backend llamado con argumentos: {filename} {idfile}")
        
        self.file_content_js = file_content
        file_bytes = bytes(file_content)
        file_stream = io.BytesIO(file_bytes)
        
        self.uploaded_files[idfile] = file_stream
        print(self.uploaded_files)
        
    # @Slot(str, list, result=str)
    # def send_order_to_server(self, command, values):
    #     print(f"send_order_to_server llamado con commando: {command}")
    #     if command == "Conseguir mas CAPTCHAs para entrenamiento":
    #         self.excel_worker = ExcelWorker(self.uploaded_files)
    #         self.excel_worker.finished.connect(self.on_processing_finished)
    #         self.excel_worker.start()
    #         return "Creacion de archivo iniciado"
    #     if command == "Divide el archivo":
    #         self.split_worker = SplitWorker(self.file_save_path, self.area_folder)
    #         self.split_worker.start()
    #         return "Division de archivo iniciado"
    #     return "Comando no reconocido"
    
    # @Slot(str)
    # def on_processing_finished(self, message):
    #     print(message)
    #     if 'Archivo Excel Creado Exitosamente!' in message:
    #         self.file_save_path = save_file_folder(save_type = 'file')
    #         area_folder = Path(self.file_save_path).resolve().parent
    #         self.area_folder = get_file_path(area_folder, "Archivos Áreas")
    #         if self.file_save_path:
    #             rename_temp_file(self.excel_worker.temp_paths['file__actual'], self.file_save_path)
    #         else:
    #             print('Guardado cancelado')
    #     if 'Archivo Pyme Creado Exitosamente!' in message:
    #         self.file_save_path = save_file_folder(save_type = 'file')
    #         if self.file_save_path:
    #             rename_temp_file(self.search_pyme.temp_paths['fileInputPyme'], self.file_save_path)
    #         else:
    #             print('Guardado cancelado')
    #     else:
    #         print(message)


#Configuracion de la aplicacion
window = QApplication(sys.argv)
view = QWebEngineView()

# Configurar WebChannel
channel = QWebChannel()
handler = CallHandler()
channel.registerObject('handler', handler)  # Registra el objeto handler

# Asignar la página personalizada para capturar console.log
page = CustomWebPage(view)
view.setPage(page)
view.page().setWebChannel(channel)  # Asignar el canal a la página

def load_html():
    html_url = QUrl.fromLocalFile(str(HTML_DIR))
    view.setUrl(html_url)
    view.reload()

load_html()
clean_folder(TEMP_DIR, '*') #Limpiar la carpeta temp cada vez que se inicia la app


#Configurar el watcher para recargar HTML y CSS
watcher = QFileSystemWatcher()
watcher.addPath(str(HTML_DIR))
watcher.addPath(str(r'C:\Users\jalvarez\Local\PMEJ\Codigos\2025\ZeusScrape\features\contact\assets\styles\styles.css'))
watcher.addPath(str(r'C:\Users\jalvarez\Local\PMEJ\Codigos\2025\ZeusScrape\features\contact\pages\page.html'))
watcher.fileChanged.connect(load_html)

view.resize(1024, 750)
view.show()

window.exec()

