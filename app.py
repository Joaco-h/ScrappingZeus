import sys
from pathlib import Path

# Importar la configuración del entorno primero
from app.configs.environment import PROJECT_ROOT
# Ahora podemos importar el resto de módulos con seguridad
from PySide6.QtCore import QUrl, QObject, Slot
from PySide6.QtWidgets import QApplication, QFileDialog
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWebEngineCore import QWebEngineProfile
from PySide6.QtWebChannel import QWebChannel
import json

# Importar las funciones correctas de tus archivos
from app.core.captcha_extractor import get_captchas_labels
from app.core.zeus_scrapping import create_pyme_file
from app.configs.configs import call_driver, site_url, ml_path, configs_path

class Backend(QObject):
    def __init__(self):
        super().__init__()
        self.temp_path = {}
        self.cell_addresses = {}

    @Slot(int)
    def extractCaptchas(self, count):
        try:
            # Usar la función existente de captcha_extractor
            get_captchas_labels(count)
            self.notify_frontend("Extracción de captchas completada")
        except Exception as e:
            self.notify_frontend(f"Error: {str(e)}")

    @Slot()
    def openFileDialog(self):
        file_name, _ = QFileDialog.getOpenFileName(
            None,
            "Seleccionar archivo Excel",
            "",
            "Excel Files (*.xlsx *.xls)"
        )
        if file_name:
            try:
                # Guardar la ruta del archivo para usarla en el scraping
                self.temp_path = {
                    'fileInputPyme': file_name,
                    'tempFile': file_name  # Puedes ajustar esto según necesites
                }
                
                # Configurar cell_addresses con valores por defecto o desde un formulario
                self.cell_addresses = {
                    'rutPyme': 'A2',  # Estos valores deberían venir del frontend
                    'namePyme': 'B2',
                    'lastRowPyme': '10',
                    'sheetname': 'Sheet1'
                }
                
                # Aquí podrías leer el archivo para mostrar los RUTs
                # Por ahora solo mostraremos un mensaje
                self.notify_frontend("Archivo cargado correctamente")
            except Exception as e:
                self.notify_frontend(f"Error al cargar el archivo: {str(e)}")

    @Slot()
    def startScraping(self):
        try:
            if not self.temp_path:
                self.notify_frontend("Por favor, carga un archivo primero")
                return

            # Usar la función existente de zeus_scrapping
            result = create_pyme_file(self.temp_path, self.cell_addresses)
            self.notify_frontend(result)
        except Exception as e:
            self.notify_frontend(f"Error: {str(e)}")

    def notify_frontend(self, message):
        js = f"alert('{message}')"
        if hasattr(self, 'page'):
            self.page.runJavaScript(js)

    def set_web_page(self, page):
        self.page = page

class WebApp(QWebEngineView):
    def __init__(self):
        super().__init__()
        self.setup_ui()
        
    def setup_ui(self):
        self.setWindowTitle("Zeus Tools")
        self.resize(1200, 800)
        
        # Configurar el perfil web
        profile = QWebEngineProfile.defaultProfile()
        profile.setPersistentCookiesPolicy(QWebEngineProfile.NoPersistentCookies)
        
        # Configurar el canal web y el backend
        self.channel = QWebChannel(self)
        self.backend = Backend()
        self.backend.set_web_page(self.page())
        self.channel.registerObject("backend", self.backend)
        self.page().setWebChannel(self.channel)
        
        # Usar PROJECT_ROOT para las rutas
        html_path = PROJECT_ROOT / "templates" / "index.html"
        self.load(QUrl.fromLocalFile(str(html_path.absolute())))

def main():
    app = QApplication(sys.argv)
    webapp = WebApp()
    webapp.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main() 