from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWebEngineCore import QWebEnginePage
from PySide6.QtWidgets import QApplication, QMainWindow
from PySide6.QtCore import QUrl, QFileSystemWatcher, Slot, QObject
from PySide6.QtWebChannel import QWebChannel

from common.configs.configs import TEMP_DIR, HTML_DIR, COMMON_CSS_DIR, FEATURES_DIR
from common.utils.funciones import io, sys, Path
# from common.utils.funciones import Path, get_file_path, clean_folder, rename_temp_file, save_file_folder

from features.pyme_finder.utils.clases import SearchPyme


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
    
    @Slot(str, list, result=str)
    def send_order_to_server(self, command, values):
        print(f"send_order_to_server llamado con commando: {command}")
        
        if command == "Predice el Captcha":
            print('Ejecutando SearchPyme...')
            self.search_pyme = SearchPyme()
            self.search_pyme.finished.connect(self.on_processing_finished)
            self.search_pyme.start()
            return "Se predijo el Captcha"
        return "Comando no reconocido"
    
    @Slot(str)
    def on_processing_finished(self, result):
        print("Resultado del hilo recibido")
        self.last_captcha_base64 = result[0]
        self.last_captcha_prediction = result[1]

    @Slot(result=str)
    def get_image_base64(self):
        return self.last_captcha_base64

    @Slot(result=str)
    def get_captcha_prediction(self):
        return self.last_captcha_prediction


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

style_hes = fr'{Path(FEATURES_DIR)}/pyme_finder/assets/styles/styles.css'
page_hes = fr'{Path(FEATURES_DIR)}/pyme_finder/pages/page.html'

#Configurar el watcher para recargar HTML y CSS
watcher = QFileSystemWatcher()
watcher.addPath(HTML_DIR)
watcher.addPath(COMMON_CSS_DIR)
watcher.addPath(style_hes)
watcher.addPath(page_hes)
watcher.fileChanged.connect(load_html)

view.resize(1024, 750)
view.show()

window.exec()
