from PySide6.QtCore import QUrl, QObject, Slot
from PySide6.QtWidgets import QApplication, QFileDialog
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWebEngineCore import QWebEngineProfile
from pathlib import Path
import sys
import json

class Backend(QObject):
    def __init__(self, web_view):
        super().__init__()
        self.web_view = web_view

    @Slot(int)
    def extractCaptchas(self, count):
        try:
            # Llamar a tu función existente de extracción de captchas
            from app.core.captcha_extractor import get_captchas_labels
            get_captchas_labels(count)
            self.notify_frontend("Extracción de captchas completada")
        except Exception as e:
            self.notify_frontend(f"Error: {str(e)}")

    @Slot()
    def openFileDialog(self):
        file_name, _ = QFileDialog.getOpenFileName(
            self.web_view,
            "Seleccionar archivo Excel",
            "",
            "Excel Files (*.xlsx *.xls)"
        )
        if file_name:
            try:
                # Procesar el archivo y obtener los RUTs
                ruts = self.process_excel_file(file_name)
                # Enviar los RUTs al frontend
                self.web_view.page().runJavaScript(
                    f"window.displayRuts({json.dumps(ruts)})"
                )
            except Exception as e:
                self.notify_frontend(f"Error al cargar el archivo: {str(e)}")

    @Slot()
    def startScraping(self):
        try:
            # Llamar a tu función existente de scraping
            from app.core.zeus_scrapping import create_pyme_file
            result = create_pyme_file(self.temp_path, self.cell_addresses)
            self.notify_frontend(result)
        except Exception as e:
            self.notify_frontend(f"Error: {str(e)}")

    def notify_frontend(self, message):
        js = f"alert('{message}')"  # Puedes mejorar esto con una UI más elegante
        self.web_view.page().runJavaScript(js)

    def process_excel_file(self, file_path):
        # Implementar la lógica para leer los RUTs del archivo Excel
        # Retornar la lista de RUTs
        pass

class WebApp(QWebEngineView):
    def __init__(self):
        super().__init__()
        self.backend = Backend(self)
        self.setup_ui()
        
    def setup_ui(self):
        # Configurar la ventana principal
        self.setWindowTitle("Zeus Tools")
        self.resize(1200, 800)
        
        # Configurar el perfil web
        profile = QWebEngineProfile.defaultProfile()
        profile.setPersistentCookiesPolicy(QWebEngineProfile.NoPersistentCookies)
        
        # Exponer el backend al JavaScript
        self.page().setWebChannel(self.backend)
        
        # Cargar el archivo HTML
        current_dir = Path(__file__).parent
        html_path = current_dir / "templates" / "index.html"
        self.load(QUrl.fromLocalFile(str(html_path.absolute())))

def main():
    app = QApplication(sys.argv)
    webapp = WebApp()
    webapp.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main() 