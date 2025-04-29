from common.utils.funciones import Path, pd, xw, extract_columns, remove_newlines, get_file_path, ensure_directory_exists, win32c
from features.pendiente_hes.configs.config_formulas import color_header, all_columns, all_formulas, all_sheets, target_formula

sheet_base = all_sheets['Sheet Base']
sheet_sap = all_sheets['Sheet Sap']
sheet_areas = all_sheets['Sheet Area']
columns = all_columns['Columns']
columns_int = all_columns['Columns Integer']
columns_float = all_columns['Columns Float']


def prepare_hes_file(path, path_prev):
    df = pd.read_excel(path,  sheet_name=sheet_sap)
    for column in all_formulas.keys():
        df[column] = None

    df = df[columns]
    for col in columns_int:
        df[col]= df[col].astype('int64')
    for col in columns_float:
        df[col]= df[col].astype(float)

    #Change Sheet Name
    with xw.App(visible=True) as app :
        wb = app.books.open(path)
        wb.sheets[sheet_sap].name = sheet_base

        #Delete Useless Sheets
        for sheet in wb.sheet_names:
            if sheet != sheet_base:
                wb.sheets[sheet].delete()

        #Clear Old Data
        ws = wb.sheets[sheet_base]
        ws.used_range.clear_contents()

        #Insert New Data
        ws = wb.sheets[sheet_base]
        ws['A1'].options(pd.DataFrame,
                        index = False, header = True, expand = 'table').value = df

        #Retrieve Coordinates
        ws = wb.sheets[sheet_base]
        range_columns = ws.range((1,1),(1,df.shape[1]))
        columns_coord = {i.value:extract_columns(i.address) for i in range_columns}

        #Change Columns Formats
        df = df[columns]
        for col in columns_int + columns_float:
            ws.range('{col}:{col}'.format(col=columns_coord[col])).number_format = '0'

        #Insert New Formulas
        ##Delete \n
        all_formulas_mod = {col:remove_newlines(formula) for col,formula in all_formulas.items()}
        for column, formula in all_formulas_mod.items():
            target_cell = columns_coord[column] + '2'
            if isinstance(target_formula[column], tuple):
                formula_cell_1 = columns_coord[target_formula[column][0]]
                formula_cell_2 = columns_coord[target_formula[column][1]]
                ws.range(target_cell).formula = formula.format(
                    value1=formula_cell_1,
                    value2=formula_cell_2)
                continue
            formula_cell = columns_coord[target_formula[column]]
            ws.range(target_cell).formula = formula.format(value=formula_cell)

        num_rows = df.shape[0]
        for col, formula in all_formulas_mod.items():
            col_letter = columns_coord[col]
            source = ws.range(col_letter+'2')
            destination = ws.range(f'{col_letter}{2}:{col_letter}{num_rows+1}')
            source.autofill(destination, type_='fill_default')

        #Format The File
        num_cols = df.shape[1]
        format_range = ws.range((1,1), (1,num_cols))

        format_range.color = color_header
        format_range.api.Borders.LineStyle = 1
        ws.used_range.api.AutoFilter(Field:=1)
        ws.used_range.api.HorizontalAlignment = xw.constants.HAlign.xlHAlignCenter
        ws.used_range.autofit()

        #Move Sheets From Previous File
        wb_previous = app.books.open(path_prev)

        for sheetname in sheet_areas[::-1]:
            sheet = wb_previous.sheets[sheetname]
            sheet.copy(after = wb.sheets[0])

        wb_previous.close()
        
        col1, col2 = format_range.address.split(':')
        col1, col2 = extract_columns(col1), extract_columns(col2)

        range_new_source = f"'{sheet_base}'!${col1}:${col2}"

        for sheet in sheet_areas:
            ws_table = wb.sheets[sheet]
            ws_table['A4'].color = (255, 217, 102)
            ws_table['I4'].color = (255, 217, 102)
            if sheet == 'Control Área Operaciones':
                ws_table['Q4'].color = (255, 217, 102)
            for idx, pt in enumerate(ws_table.api.PivotTables()):
                pivot_table = ws_table.api.PivotTables(pt.Name)
                pivot_table.ChangePivotCache(wb.api.PivotCaches().Create(
                    SourceType=win32c.xlDatabase,
                    SourceData=range_new_source,
                    Version=win32c.xlPivotTableVersion12
                    ))
        wb.save(path)


def copy_sheets_to_individual_files(file_path, folder_path):
    with xw.App(visible=True) as app:
        wb = app.books.open(file_path)
        for sheet in wb.sheets:
            if sheet.name == 'Base General': continue
            new_wb = xw.Book()
            sheet.api.Copy(Before=new_wb.sheets[0].api)
            new_wb.sheets[1].api.Delete()
            #Ensure the directory exists
            ensure_directory_exists(folder_path)
            new_path_split = get_file_path(folder_path, sheet.name) 
            new_wb.save(f'{new_path_split}.xlsx')
            new_wb.close()
