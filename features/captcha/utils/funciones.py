from common.utils.funciones import handler_excel_errors
from features.pendiente_hes.core.main import prepare_hes_file, copy_sheets_to_individual_files


@handler_excel_errors
def split_excel_file(file_path, folder_path):
    try:
        copy_sheets_to_individual_files(file_path, folder_path)
        return 'Archivo Excel Creado Exitosamente!'
    
    except PermissionError as e:
        return f'Error de Permisos: {e}'
    except FileNotFoundError as e:
        return f'Archivo no encontrado: {e}'
    except Exception as e:
        return f'Ocurrio un error innesperado: {e}'

@handler_excel_errors
def create_excel_file(paths):
    try:
        prepare_hes_file(paths["file__actual"], paths["file__previo"])
        return 'Archivo Excel Creado Exitosamente!'
    
    except PermissionError as e:
        return f'Error de Permisos: {e}'
    except FileNotFoundError as e:
        return f'Archivo no encontrado: {e}'
    except Exception as e:
        return f'Ocurrio un error innesperado: {e}'