from utils.funciones import *
from utils.settings import ml_path, configs_path, site_url, driver_path

def web_scrapping(file, missing_suppliers, suppliers, suppliers_sheet):
    site_url = r'https://zeus.sii.cl/cvc/stc/stc.html'
    driver_path = r'C:\Users\jalvarez\Downloads\edgedriver_win64 (2)\msedgedriver.exe'
    
    edge_options = Options()
    edge_options.add_argument('--log-level=3')
    
    service = Service(executable_path=driver_path)
    driver_edge = webdriver.Edge(service=service, options=edge_options)
    driver_edge.get(site_url)
    
    #Busca en zeus los nombres e identifica si es una pyme o no basado en el rut
    try:
        for index, row in missing_suppliers.iterrows():
            for _ in range(3):
                print(row['Rut'])
                rut = str(row['Rut']).replace('−','-').split('-')[0]
                dv = calcular_dv(rut)
                captcha = input('Por favor, ingrese el código CAPTCHA:')
                textboxes = get_textboxes(driver_edge)
                captcha_image = enter_captcha(driver_edge, textboxes, rut, dv, captcha)
                if handle_alert(driver_edge, captcha):
                    continue
                try:
                    wait = WebDriverWait(driver_edge, 10)
                    wait.until(EC.staleness_of(textboxes['captcha']))
                    
                    elementos = driver_edge.find_elements(By.TAG_NAME, 'div')
                    texto = elementos[1].text
                    nombre, es_pyme = extraer_informacion(texto)
                    print(f'Nombre o Razón Social: {nombre}')
                    print(f'Es PYME: {es_pyme}')
                    missing_suppliers.loc[index, 'Nombre Proveedor'] = nombre
                    missing_suppliers.loc[index, 'Pyme'] = es_pyme
                    
                    driver_edge.get(site_url)
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
    
    #Agrega los proveedores faltante al archivo de excel
    try:
        app = xw.App(visible=False)
        wb = app.books.open(file)
        ws = wb.sheets[suppliers_sheet]
        
        missing_suppliers = missing_suppliers.rename({
            'Rut':'Cuenta',
            'Nombre Proveedor':'Empresa',
        }, axis = 1)
        
        suppliers = pd.concat([missing_suppliers, suppliers])
        suppliers = suppliers.drop_duplicates(subset = ['Cuenta'])
        suppliers = suppliers.sort_values(['Pyme','Cuenta'], ascending=[True, True])
        suppliers = suppliers.map(lambda x: x.strip().upper() if isinstance(x, str) else x)
        
        ws_range = ws.used_range.address
        ws_range = ws_range.replace('$A$1','$A$2')
        ws.range(ws_range).clear_contents()
        ws.range('A2').options(index=False, header=False).value = suppliers
        wb.save(file)
    finally:
        app.quit()

def get_captchas_labels(meta):
    rut='19738907'
    dv='9'
    
    site_url = 'https://zeus.sii.cl/cvc/stc/stc.html'
    driver_path = r'C:\Users\jalvarez\Downloads\edgedriver_win64 (2)\msedgedriver.exe'
    data_path = 'W:\\06. Finanzas\\02.- Finanzas\\Joaquin Alvarez\\Codigos\\Cuentas por Pagar\\Training Data'
    
    driver_edge = setup_driver(driver_path)
    driver_edge.get(site_url)
    
    try:
        for _ in range( meta - len(os.listdir(data_path)) ):
            for _ in range(3):
                captcha = input('Por favor, ingrese el código CAPTCHA:')
                textboxes = get_textboxes(driver_edge)
                captcha_image = enter_captcha(driver_edge, textboxes, rut, dv, captcha)
                if handle_alert(driver_edge, captcha):
                    continue
                try:
                    wait = WebDriverWait(driver_edge, 10)
                    wait.until(EC.staleness_of(textboxes['captcha']))
                    data = get_file_path(data_path, captcha[:4])
                    captcha_image.save(f'{data}.png')
                    driver_edge.get(site_url)
                    print(f'Se han etiquetado {len(os.listdir(data_path))}'
                        f' imagenes faltan {meta - len(os.listdir(data_path))}')
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


# def get_captchas_labels_ml_test(meta):

path = r'W:\06. Finanzas\03.- Gestión\08.- Otros\Control Costos\Controles Semestrales\Maestro Proveedores\01\Pyme.xlsx'



service = Service(executable_path=driver_path)
driver_edge = webdriver.Edge(service=Service(EdgeChromiumDriverManager().install()), options=edge_options)    
driver_edge.get(site_url)

configs = BaseModelConfigs.load(configs_path)
configs.model_path = ml_path
model = ImageToWordModel(model_path=configs.model_path, char_list=configs.vocab)

df = pd.read_excel(path, sheet_name='Hoja1')
ruts = df['Rut'].drop_duplicates().reset_index(drop=True)

#TESTS WITH BAD RUTS
##ADD BAD RUTS AT FIRST ROW
ruts = pd.concat([pd.Series('k'), ruts], ignore_index=True)
ruts = pd.concat([pd.Series('19738907-9'), ruts], ignore_index=True)
ruts = pd.concat([pd.Series('19738907'), ruts], ignore_index=True)
##ADD BAD RUTS AT LAST ROW
ruts = pd.concat([ruts, pd.Series('k')], ignore_index=True)

i = 0
ruts_pyme = []

start_time = time.time()
while i < len(ruts):
    rut = str(ruts[i]).replace('−','-').split('-')[0]
    dv = calcular_dv(rut)
    
    #CHECK IF RUT IS ALREADY PROCESS
    if any(d['rut']==f'{rut}-{dv}' for d in ruts_pyme):
        print(f'El Rut {rut} ya existe en ruts_pyme, saltando a la siguiente iteracion.')
        i+=1
        continue
    
    #SEND INPUTS TO THE WEBSITE
    textboxes = get_textboxes(driver_edge)
    image = get_captcha_image(driver_edge)
    captcha = model.predict(image)
    send_keys(textboxes, rut, dv, captcha)

    alert = handle_alert(driver_edge) #En caso de ingresar un rut/captcha invalido se acepta la alerta del buscador
    
    if alert == 'R':
        i+=1
        driver_edge.refresh()
        ruts_pyme.append({'rut': rut,'nombre': np.nan, 'pyme': np.nan})
        continue
    
    if alert =='C':
        driver_edge.refresh()
        continue
    
    #GET THE INFO
    elements = driver_edge.find_elements(By.TAG_NAME, 'div')
    text = elements[1].text
    name, pyme = extraer_informacion(text)
    
    print(f'Nombre o Razón Social: {name}')
    print(f'Es PYME: {pyme}')
    
    ruts_pyme.append({'rut': rut + '-' + dv, 'nombre':name ,'pyme':pyme})

    image = cv2.resize(image, (image.shape[1] * 4, image.shape[0] * 4))
    # cv2.imshow(captcha, image)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()
    driver_edge.get(site_url)
    
    i+=1

end_time = time.time()

print(f'Registros buscados: {len(ruts)}')
print(f'Tiempo de ejecución: {end_time - start_time} segundos')

df_ruts_pyme = pd.DataFrame(ruts_pyme)
df_ruts_pyme.drop_duplicates(subset='rut', inplace=True)
df_ruts_pyme.to_excel(r'W:\06. Finanzas\03.- Gestión\08.- Otros\Control Costos\Controles Semestrales\Maestro Proveedores\01\test.xlsx', index=False)