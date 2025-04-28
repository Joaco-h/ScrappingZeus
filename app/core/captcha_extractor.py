from app.utils.clases import SalirBucle
from app.utils.funciones import os, EC, WebDriverWait, TimeoutException, enter_captcha, get_textboxes, handle_alert, get_file_path
from app.configs.configs import call_driver, DATA_DIR


def get_captchas_labels(meta):
    rut='19738907'
    dv='9'

    site_url = 'https://zeus.sii.cl/cvc/stc/stc.html'

    driver_edge = call_driver()
    driver_edge.get(site_url)

    try:
        for _ in range( meta - len(os.listdir(DATA_DIR)) ):
            for _ in range(3):
                captcha = input('Por favor, ingrese el código CAPTCHA:')
                textboxes = get_textboxes(driver_edge)
                captcha_image = enter_captcha(driver_edge, textboxes, rut, dv, captcha)
                # if handle_alert(driver_edge):
                #     continue
                try:
                    wait = WebDriverWait(driver_edge, 10)
                    wait.until(EC.staleness_of(textboxes['captcha']))
                    data = get_file_path(DATA_DIR, captcha[:4])
                    captcha_image.save(f'{data}.png')
                    driver_edge.get(site_url)
                    print(f'Se han etiquetado {len(os.listdir(DATA_DIR))}'
                        f' imagenes faltan {meta - len(os.listdir(DATA_DIR))}')
                    break
                except TimeoutException:
                    print('El CAPTCHA ingresado fue incorrecto.'
                        ' Por favor, inténtelo de nuevo.')
                except Exception as e:
                    print(f'Error : {e}')
            else:
                print('Demasiados intentos fallidos.')
                break
    except SalirBucle:
        print('Saliendo del bucle...')
    finally:
        driver_edge.quit()

if __name__ == '__main__':
    get_captchas_labels(2500)
