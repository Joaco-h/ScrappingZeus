from common.utils.funciones import np, typing, handler_excel_errors
from features.pyme_finder.utils.funciones import (cv2, BaseModelConfigs, OnnxInferenceModel, ctc_decoder, get_captcha_image)
from features.pyme_finder.configs.config_scrapping import site_url, call_driver
from features.pyme_finder.configs.config_ml import ml_path, configs_path

class SalirBucle(Exception):
    pass

class ImageToWordModel(OnnxInferenceModel):
    def __init__(self, char_list: typing.Union[str, list], *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.char_list = char_list
    
    
    def predict(self, image: np.ndarray):
        image = cv2.resize(image, self.input_shapes[0][1:3][::-1])
        image_pred = np.expand_dims(image, axis=0).astype(np.float32)
        preds = self.model.run(self.output_names, {self.input_names[0]: image_pred})[0]
        text = ctc_decoder(preds, self.char_list)[0]
        return text

def scrape_rut_info():
    driver_chrome = call_driver()
    driver_chrome.get(site_url)
    
    configs = BaseModelConfigs.load(configs_path)
    configs.model_path = ml_path
    model = ImageToWordModel(model_path=configs.model_path, char_list=configs.vocab)
    
    keep_going = True
    
    while keep_going:
        #SEND INPUTS TO THE WEBSITE
        image = get_captcha_image(driver_chrome)
        captcha = model.predict(image)
        
        image = cv2.resize(image, (image.shape[1] * 4, image.shape[0] * 4))
        cv2.imshow(captcha, image)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
        driver_chrome.get(site_url)
        
        i+=1

@handler_excel_errors
def create_pyme_file():
    try:
        scrape_rut_info()
        return 'Archivo Pyme Creado Exitosamente!'
    
    except PermissionError as e:
        return f'Error de Permisos: {e}'
    except FileNotFoundError as e:
        return f'Archivo no encontrado: {e}'
    except Exception as e:
        return f'Ocurrio un error innesperado: {e}'