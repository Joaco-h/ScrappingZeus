from utils.functions import np, cv2, time, typing, Image, BytesIO, By, OnnxInferenceModel, BaseModelConfigs
from utils.functions import get_captcha_image, ctc_decoder
from configs.config_scrapping import site_url, call_driver
from configs.config_ml import ml_path, configs_path

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
    
    start_time = time.time()
    while True:
        
        image = get_captcha_image(driver_chrome)
        captcha = model.predict(image)
                
        image = cv2.resize(image, (image.shape[1] * 4, image.shape[0] * 4))
        cv2.imshow(captcha, image)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
        driver_chrome.get(site_url)
        

if __name__ == "__main__":
    scrape_rut_info()