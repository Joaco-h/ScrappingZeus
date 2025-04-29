from features.pyme_finder.utils.funciones import webdriver, Service, ChromeDriverManager

site_url = 'https://zeus.sii.cl/cvc/stc/stc.html'

def call_driver():
    chrome_options = webdriver.ChromeOptions()
    # chrome_options.add_argument('headless')
    chrome_options.add_argument('--log-level=3')
    
    service = Service(ChromeDriverManager().install())
    return  webdriver.Chrome(service=service, options=chrome_options)