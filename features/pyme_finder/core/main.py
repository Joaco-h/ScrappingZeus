from common.configs.configs import TEST_DIR
from common.utils.funciones import np, pd, time, Path, typing, extract_rut_before_dash, calcular_dv, extract_text, extract_number, get_cell_value, handler_excel_errors
from features.pyme_finder.utils.funciones import (cv2, By, EC, WebDriverWait, BaseModelConfigs, OnnxInferenceModel, ctc_decoder, get_textboxes, get_captcha_image, send_keys, handle_alert, extraer_informacion)
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

def format_pyme_temp_file(temp_path, cellAddresses):
    name_file, path_file = list(temp_path.items())[0]
    rut_column = extract_text(cellAddresses['rutPyme'])
    name_column = extract_text(cellAddresses['namePyme']) if cellAddresses['namePyme'] else rut_column
    first_row = extract_number(cellAddresses['rutPyme'])
    lastrow = extract_number(cellAddresses['lastRowPyme'])
    sheet_name = cellAddresses['sheetname']
    
    df = pd.read_excel(
        path_file,
        sheet_name=sheet_name, 
        usecols=f'{rut_column}:{name_column}',
        skiprows=first_row-1,
        nrows=lastrow
        )
    
    rut_value = get_cell_value(path_file, sheet_name, cellAddresses['rutPyme'])
    name_value = get_cell_value(path_file, sheet_name, cellAddresses['namePyme']) if cellAddresses['namePyme'] else False
    
    return df, rut_value, name_value

def scrape_rut_info(temp_path, cellAddresses):
    driver_chrome = call_driver()
    driver_chrome.get(site_url)
    
    configs = BaseModelConfigs.load(configs_path)
    configs.model_path = ml_path
    model = ImageToWordModel(model_path=configs.model_path, char_list=configs.vocab)
    
    df, rut_col, name_col = format_pyme_temp_file(temp_path, cellAddresses)
    print('----------------------------------------------------------------')
    print(rut_col, name_col)
    print('----------------------------------------------------------------')
    print(df)
    print('----------------------------------------------------------------')
    ruts = df[rut_col].drop_duplicates().reset_index(drop=True)
    
    #TESTS WITH BAD RUTS          
    #ADD BAD RUTS AT FIRST ROW
    # ruts = pd.concat([pd.Series('k'), ruts], ignore_index=True)
    # ruts = pd.concat([pd.Series('19738907-9'), ruts], ignore_index=True)
    # ruts = pd.concat([pd.Series('19738907'), ruts], ignore_index=True)
    # ##ADD BAD RUTS AT LAST ROW
    # ruts = pd.concat([ruts, pd.Series('k')], ignore_index=True)
    
    i = 0
    ruts_pyme = []
    
    start_time = time.time()
    while i < len(ruts):
        rut = str(ruts[i]).replace('−','-').split('-')[0]
        dv = calcular_dv(rut)
        
        #CHECK IF RUT IS ALREADY PROCESS
        if any(d['Rut']==f'{rut}-{dv}' for d in ruts_pyme):
            print(f'El Rut {rut} ya existe en ruts_pyme, saltando a la siguiente iteracion.')
            i+=1
            continue
        
        #SEND INPUTS TO THE WEBSITE
        textboxes = get_textboxes(driver_chrome)
        image = get_captcha_image(driver_chrome)
        captcha = model.predict(image)
        send_keys(textboxes, rut, dv, captcha)
        
        alert = handle_alert(driver_chrome) #En caso de ingresar un rut/captcha invalido se acepta la alerta del buscador
        
        if alert == 'R':
            i+=1
            driver_chrome.refresh()
            ruts_pyme.append({'Rut': rut,'Nombre Zeus': np.nan, 'Pyme': np.nan})
            continue
        
        if alert =='C':
            driver_chrome.refresh()
            continue
        
        #GET THE INFO
        elements = WebDriverWait(driver_chrome, 10).until(
                EC.presence_of_all_elements_located((By.TAG_NAME, 'div'))
            )
        text = elements[0].text
        name, pyme = extraer_informacion(text)
        
        print(f'Nombre o Razón Social: {name}')
        print(f'Es PYME: {pyme}')
        
        ruts_pyme.append({'Rut': rut + '-' + dv, 'Nombre Zeus':name , 'Pyme':pyme})
        
        # image = cv2.resize(image, (image.shape[1] * 4, image.shape[0] * 4))
        # cv2.imshow(captcha, image)
        # cv2.waitKey(0)
        # cv2.destroyAllWindows()
        driver_chrome.get(site_url)
        
        i+=1
    
    end_time = time.time()
    
    print(f'Registros buscados: {len(ruts)}')
    print(f'Tiempo de ejecución: {end_time - start_time} segundos')
    
    df_ruts_pyme = pd.DataFrame(ruts_pyme)
    df_ruts_pyme.sort_values(by='Rut', ascending=True, inplace=True)
    df_ruts_pyme.drop_duplicates(subset='Rut', inplace=True)
    df_ruts_pyme['Rut sin Dv'] = df_ruts_pyme['Rut'].apply(extract_rut_before_dash)
    
    if name_col:
        df['Rut sin Dv'] = df[rut_col].apply(extract_rut_before_dash)
        df_ruts_pyme = df_ruts_pyme.merge(df, on='Rut sin Dv', how='left')
        df_ruts_pyme.dropna(subset='Rut', inplace=True)
        df_ruts_pyme.drop_duplicates(subset='Rut', inplace=True)
        df_ruts_pyme[name_col+'Nuevo'] = np.where(
            df_ruts_pyme['Nombre Zeus'] != '**',
            df_ruts_pyme['Nombre Zeus'],
            df_ruts_pyme[name_col])
        df_ruts_pyme = df_ruts_pyme[['Rut', 'Rut sin Dv', name_col+'Nuevo', 'Pyme']]
        df_ruts_pyme.rename({name_col+'Nuevo': name_col}, axis=1, inplace=True)
    
    df_ruts_pyme = df_ruts_pyme[['Rut', 'Rut sin Dv', name_col, 'Pyme']]
    df_ruts_pyme.to_excel(temp_path['fileInputPyme'], sheet_name='Pyme', index=False)

@handler_excel_errors
def create_pyme_file(temp_path, cellAddresses):
    try:
        scrape_rut_info(temp_path, cellAddresses)
        return 'Archivo Pyme Creado Exitosamente!'
    
    except PermissionError as e:
        return f'Error de Permisos: {e}'
    except FileNotFoundError as e:
        return f'Archivo no encontrado: {e}'
    except Exception as e:
        return f'Ocurrio un error innesperado: {e}'