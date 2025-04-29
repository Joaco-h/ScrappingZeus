from app.utils.funciones import (
    EC, WebDriverWait, TimeoutException,
    fill_form_fields, fetch_captcha_image,
    get_textboxes, handle_alert)
from app.configs.configs import call_driver, DATA_DIR

class CaptchaCollector:
    def __init__(self, meta=2500, rut='19738907', dv='9'):
        self.meta = meta
        self.rut = rut
        self.dv = dv
        self.site_url = 'https://zeus.sii.cl/cvc/stc/stc.html'
        self.unique_captchas = set()
        self.data_dir = DATA_DIR/ 'captcha_images_v1'
        self._load_existing_captchas()
        
    def _load_existing_captchas(self):
        """Carga los captchas existentes desde la carpeta a el set de monitore"""
        for captcha_file in self.data_dir.glob('*.png'):
            self.unique_captchas.add(captcha_file.stem)
    
    def get_remaining(self):
        """Obtener los CAPTCHAs restantes"""
        return self.meta - len(self.unique_captchas)
    
    def _save_captchas(self, captcha_img, captcha_code):
        """Guardar la imagen captcha"""
        captcha_path = self.data_dir / f"{captcha_code}.png"
        captcha_img.save(captcha_path)
        return captcha_path

    def process_captcha(self, driver):
        """
        Procesa un elemento CAPTCHA incluyendo el input de usuario y el guardado de la imagen

        Return:
            tuple: (bool success, bool was_replacement)
        """
        try:
            captcha = input('Por favor, ingresa el código CAPTCHA:')
            textboxes = get_textboxes(driver)
            
            # Guarda en memoria el CAPTCHA antes de enviar el formulario
            captcha_img = fetch_captcha_image(driver, array=False)
            
            #Llenar y enviar el formulario
            fill_form_fields(driver, textboxes, self.rut, self.dv, captcha)
            
            # Manejar la alerta si aparece
            if not handle_alert(driver) == 'N':
                print("Alerta detectada, reintendando...")
                return False, False
            
            # Esperar a la respuesta del submit
            wait = WebDriverWait(driver, 10)
            wait.until(EC.staleness_of(textboxes['captcha']))
            
            captcha_code = captcha[:4]
            # Checkear si este captcha ya existe
            was_replacement = captcha_code in self.unique_captchas
            
            # Guardar CAPTCHA exitoso
            saved_path = self._save_captchas(captcha_img, captcha_code)
            
            # Monitorea el CAPTCHA
            self.unique_captchas.add(captcha_code)
            
            # Actualizacion de estado
            if was_replacement:
                print(f"CAPTCHA {captcha_code} reemplazado en {saved_path}")
            else:
                print(f"Nuevo CAPTCHA {captcha_code} guardado en {saved_path}")
            
            return True, was_replacement
        
        except TimeoutException:
            print("Tiempo de espera agotado, reintentando...")
            return False, False
        except Exception as e:
            print(f"Error inesperado: {e}")
            return False, False
    
    def run(self):
        "Ejecutar el proceso de recoleccion de CAPTCHA"
        try:
            # Asegura que el directorio de datos existe
            self.data_dir.mkdir(parents=True, exist_ok=True)
            
            driver = call_driver()
            print(f"\nIniciando recoleccion de CAPTCHAs...")
            print(f"Directorio de datos: {self.data_dir}")
            print(f"Meta: {self.meta}")
            print(f"CAPTCHAS únicos actuales: {len(self.unique_captchas)}")
            print(f"Restantes: {self.get_remaining()}\n")
            
            while self.get_remaining() > 0:
                driver.get(self.site_url)
                success, was_replacement = self.process_captcha(driver)
                
                if success and not was_replacement:
                    remaining = self.get_remaining()
                    progress = ((self.meta - remaining) / self.meta) * 100
                    print(f"Progreso: {self.meta - remaining}/{self.meta} ({progress:.1f}%)")
                    print(f"Restantes: {remaining}\n")
        
        except KeyboardInterrupt:
            print("\nProceso interrumpido por el usuario")
        except Exception as e:
            print(f"Error fatal: {e}")
        finally:
            if 'driver' in locals():
                driver.quit()
            print(f"\nProceso finalizado.")
            print(f"Total CAPTCHAs únicos: {len(self.unique_captchas)}")
            print(f"Restantes para la meta: {self.get_remaining()}")

def main(meta=2500, rut='19738907', dv='9'):
    collector = CaptchaCollector(meta=meta, rut=rut, dv=dv)
    collector.run()

if __name__ == "__main__":
    main()

