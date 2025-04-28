from funciones import *

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

class ExcelModifier():
    def __init__(self, columns):
        self.wb = None
        self.ws = None
        self.df = None
        self.app = None
        self.file = None
        self.df_kz = None
        self.df_db = None
        self.show_file = False
        self.sheet_name_db = None
        self.columns = columns
        self.columns_ws1 = list(self.columns.keys())
        self.columns_ws2 = list(self.columns.values())
        self.sheet_position = {}
        self.address_formula = {}
        self.columns_address = {}
        self.columns_position = {}
        self.columns_db = []
        self.wb_previous = None
        self.df_previous = None
        self.file_previous = None

    def get_df_kz(self):
        df_kz = self.df[self.df[self.columns_ws1[2]] == 'KZ']
        df_kz = df_kz.rename({self.columns_ws1[7]: self.columns_ws1[7] + '2'}, axis = 1)
        self.df_kz = df_kz

    def get_df_clean(self):
        df = self.df.merge(self.df_kz[[self.columns_ws1[-3], self.columns_ws1[7]+'2']],
                           on = self.columns_ws1[-3], how = 'left')
        df = df.dropna(subset = self.columns_ws1[7] + '2')
        self.df = df

    def get_df_db(self):
        df_db = self.df[self.df[self.columns_ws1[2]] != 'KZ']
        df_db = df_db.drop(self.columns_ws1[7], axis = 1)
        df_db = df_db.rename({self.columns_ws1[7] + '2': self.columns_ws1[7]}, axis = 1)
        df_db = df_db.rename(self.columns, axis = 1)
        self.df_db = df_db

    def move_sheets(self, new_name):
        try:
            self.app = xw.App(visible=self.show_file)
            target_file = xw.Book()
            self.wb_previous = self.app.books.open(self.file_previous)

            wb_sap = self.app.books.open(self.file)
            sheet_sap = wb_sap.sheets['Sheet1']
            sheet_sap.copy(before = target_file.sheets[0], name = new_name)

            for sheetname, pos in self.sheet_position.items():
                sheet = self.wb_previous.sheets[sheetname]
                sheet.copy(before = target_file.sheets[pos])

            wb_sap.close()
            target_file.save(self.file)
        finally:
            self.app.quit()

    def update_references_on_cells(self):
        try:
            self.app = xw.App(visible=self.show_file)
            self.wb = self.app.books.open(self.file)
            path_bracket = path_format_with_bracket(self.file)
            path_bracket_previous = path_format_with_bracket(self.file_previous)
            for sheet in self.wb.sheets:
                ws = self.wb.sheets[sheet]
                ws.used_range.api.Replace(self.file_previous, self.file)
                ws.used_range.api.Replace(path_bracket_previous, path_bracket)
                self.wb.save(self.file)
        finally:
            self.app.quit()

    def retrivieng_all_coordinates(self, columns_list : list) -> None:
        """
        Obtiene todas las coordenadas de las columnas objetivo.

        Args:
            columns_list (list): Una lista con todos los diccionario que utiliza
            para encontrar las columnas donde se encuentran las columnas obj.
        """
        try:
            self.app = xw.App(visible=self.show_file)
            self.wb = self.app.books.open(self.file)
            for cell in self.ws.range('2:2'):
                if cell.value in columns_list:
                    self.columns_address[cell.value] = cell.address
            self.wb.save(self.file)
        finally:
            self.app.quit()

    def write_df_on_file(self, month, year):
        try:
            self.app = xw.App(visible=self.show_file)
            self.wb = self.app.books.open(self.file)

            self.wb.sheets.add(f'{month} {year}', before = 3)
            self.wb.sheets.add(f'KZ {month} {year}', before = 4)

            df_sheet = self.wb.sheets(f'{month} {year}')
            df_sheet_kz = self.wb.sheets(f'KZ {month} {year}')

            df_sheet['A1'].options(pd.DataFrame,
                                index = False, header = True, expand='table').value = self.df
            df_sheet_kz['A1'].options(pd.DataFrame,
                                index = False, header = True, expand='table').value = self.df_kz

            self.wb.save(self.file)

        finally:
            self.app.quit()

    def write_formula_on_file(self):
        """
        Genera las formulas que deben ir en el archivo de excel.
        En los If 
        Si entra en 1 la formula solo se escribe en la primera fila
        Si entra en 3 la formula solo se escribe en la tercera fila
        Por ultimo si entre en else statement se escribe en la fila 3 y en la fila 1, 
        en la fila 1 se rescribe el rango al que lee al formula para que considere todos los valores.
        """
        columns_positionformula = {
            'Tipo Doc':3, '# P-E':3, '# P-E/R':0, 'Plazo':3, 'Monto':1, 'Moneda':1, 'Texto':1,
            'Nombre Proveedor':3, 'Pyme':3
        }
        try:
            app = xw.App(visible=self.show_file)
            wb = app.books.open(self.file)
            ws = wb.sheets[self.sheet_name_db]
            retrivieng_columns = list(columns_positionformula.keys())
            start_address, end_address = extract_address_from_range(ws.used_range.address)
            self.start_row, self.end_row = extract_row(start_address), extract_row(end_address)
            self.start_col,self.end_col = extract_columns(start_address),extract_columns(end_address)

            for cell in ws.range(f'{self.start_col}2:{self.end_col}2'):
                if cell.value in retrivieng_columns:
                    self.columns_position[cell.value] = extract_columns(cell.address)

            for key, value in columns_positionformula.items():
                if value == 1:
                    self.address_formula[
                        self.columns_position[key] + '1'] = ws.range(
                            self.columns_position[key] + '1').formula
                elif value == 3:
                    self.address_formula[
                        self.columns_position[key] + '3'] = ws.range(
                            self.columns_position[key] + '3').formula
                else:
                    self.address_formula[
                        self.columns_position[key] + '1'] = ws.range(
                            self.columns_position[key] + '1').formula
                    self.address_formula[
                        self.columns_position[key] + '3'] = ws.range(
                            self.columns_position[key] + '3').formula
            wb.save(self.file)
        finally:
            app.quit()

    def clean_old_data(self):
        try:
            app = xw.App(visible=self.show_file)
            wb = app.books.open(self.file)
            ws = wb.sheets[self.sheet_name_db]

            start_row_values = str(int(self.start_row) + 2)
            ws.range(f'{self.start_col}{self.start_row}:'
                    f'{self.end_col}{self.start_row}').clear_contents()
            ws.range(f'{self.start_col}{start_row_values}:'
                    f'{self.end_col}{self.end_row}').clear_contents()
            wb.save(self.file)
        finally:
            app.quit()

    def update_formulas_to_new_period(self):
        path_bracket = path_format_with_bracket(self.file[3:])
        path_bracket_previous = path_format_with_bracket(self.file_previous[3:])
        
        for address, formula in self.address_formula.items():
            new_formula = formula.replace(
                self.file_previous[3:], self.file[3:])
            new_formula = new_formula.replace(
                path_bracket_previous, path_bracket)
            self.address_formula[address] = new_formula

    def write_new_data_file(self, row_number):
        try:
            app = xw.App(visible=self.show_file)
            wb = app.books.open(self.file)
            ws = wb.sheets(self.sheet_name_db)

            ws['A3'].options(pd.DataFrame,
                                index = False, header = False, expand='table').value = self.df_db

            for address, formula in self.address_formula.items():
                if 'SUBTOTAL' in formula:
                    ws.range(address).value = change_last_value(formula, row_number + 2)
                else:
                    ws.range(address).value = formula
                if '3' in address:
                    address_column = extract_letters_numbers(address)[0]
                    ws.range(address).api.AutoFill(
                        ws.range(f'{address}:{address_column}{row_number + 2}'
                                    ).api, AutoFillType.xlFillDefault)
            wb.save(self.file)
        finally:
            app.quit()

class DatesFormat():
    """
    Clase que maneja los formatos de fechas.
    """
    def __init__(self, month, year):
        self.month = get_month(month)
        self.month_on_year = range(1,13)
        self.month_two_digits = format_two_digits(month)
        self.long_year, self.short_year = get_year(year)
        self.update_date = datetime(int(self.long_year), int(self.month), 1, 0, 0)
        self.period = self.month_two_digits + '-' + self.long_year
        self.period_previous = get_previous_period(self.period)
        self.month_previous, self.year_previous = self.period_previous.split('-')


# class InterfazFileLocator:
#     def __init__(self, ventana):
#         self.ventana = ventana
#         self.ventana.title("Procesamiento de Información")
#         self.mes = None
#         self.anio = None
#         self.reprocess = None
#         self.sociedad = None

#         # Etiqueta y botones para procesar toda la información
#         label = tk.Label(ventana, text="¿Desea procesar toda la información?")
#         label.pack()

#         button_si = tk.Button(ventana, text="Sí", command=self.procesar_toda_info)
#         button_no = tk.Button(ventana, text="No", command=self.reprocesar_info)
#         button_si.pack()
#         button_no.pack()
        
#         #Caja de opciones para seleccionar la sociedad
#         self.sociedad_var = tk.StringVar(ventana)
#         self.sociedad_var.set('Seleccione una sociedad')
#         opciones_sociedad = ['TM', 'PM', 'Ambas']
#         self.opciones_menu = tk.OptionMenu(ventana, self.sociedad_var, *opciones_sociedad)
#         self.opciones_menu.pack()

#     def procesar_toda_info(self):
#         confirm = messagebox.askyesno("Confirmación", "¿Está seguro? Es posible que se pierda información de algunos proveedores.")
#         if confirm:
#             # Aquí puedes realizar acciones adicionales según la confirmación
#             print("Procesando toda la información")
#             self.reprocess = False
#             self.ventana.destroy()
#         else:
#             print("Procesamiento cancelado")

#     def reprocesar_info(self):
#         # Aquí puedes implementar la lógica para el caso de "No"
#         # Por ejemplo, crear más widgets para ingresar año y mes
#         print("Reprocesando información")

#         label_mes = tk.Label(self.ventana, text = 'Ingrese el mes (1-12):')
#         label_mes.pack()
#         self.entry_mes = tk.Entry(self.ventana)
#         self.entry_mes.pack()

#         label_anio = tk.Label(self.ventana, text='Ingrese el año (ej. 2023):')
#         label_anio.pack()
#         self.entry_anio = tk.Entry(self.ventana)
#         self.entry_anio.pack()

#         button_procesar = tk.Button(self.ventana, text = 'Procesar', command=self.procesar_fecha_sociedad)
#         button_procesar.pack()

#     def procesar_fecha_sociedad(self):
#         self.reprocess = True
#         mes = self.entry_mes.get()
#         anio = self.entry_anio.get()
#         sociedad = self.sociedad_var.get()

#         if not mes.isdigit() or int(mes) < 1 or int(mes) > 12:
#             messagebox.showerror('Error', 'El mes debe ser un número entero entre 1 y 12.')
#             return

#         if not anio.isdigit() or len(anio) != 4:
#             messagebox.showerror('Error', 'El año debe ser un número entero de 4 dígitos.')
#             return

#         if sociedad == 'Seleccione una sociedad':
#             messagebox.showerror('Error' , 'Debe seleccionar una sociedad.')
#             return
#         print(f'Procesando información para el mes {mes} del año {anio}'
#               f' de la sociedad {sociedad}...')

#         #Guardar como variables de instancias
#         self.mes = mes
#         self.anio = anio

#         #Cerrar la interfaz
#         self.ventana.destroy()

#     def get_mes(self):
#         return self.mes

#     def get_anio(self):
#         return self.anio

#     def get_reprocess(self):
#         return self.reprocess

#     def get_sociedad(self):
#         sociedad  = self.sociedad_var.get()
#         if sociedad == 'TM':
#             return ['TM']
#         elif sociedad == 'PM':
#             return ['PM']
#         else:
#             return ['PM', 'TM']
