import os

#WEB SCRAPPING
site_url = 'https://zeus.sii.cl/cvc/stc/stc.html'
driver_path = r'C:\Users\jalvarez\Downloads\edgedriver_win64 (2)\msedgedriver.exe'

#MACHINE LEARNING
ml_path = r'C:\Users\jalvarez\Local\PMEJ\Codigos\2024\Cuentas por Pagar Aut SAP\ml\models\02_captcha_to_text\202407231124'
model_path = os.path.join(ml_path, 'model.h5')
configs_path = os.path.join(ml_path, 'configs.yaml')