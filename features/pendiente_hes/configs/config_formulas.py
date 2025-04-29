color_header = (221, 221, 221)
tablas_dinamicas = ['Tabla din']


#SHEETS
sheet_base = 'Base General'
sheet_sap = 'Sheet1'
sheet_areas = [
    'Control Área Adm & Finanzas',
    'Control Área Informática',
    'Control Área Comercial',
    'Control Área Sustentabilidad',
    'Control Área Operaciones',
    'Control Área Personas',
    'Control Área SSO',
]

all_sheets = {
    'Sheet Sap': sheet_sap,
    'Sheet Base': sheet_base,
    'Sheet Area': sheet_areas,
}

#COLUMNS
columns = [
    'HES',
    'Organización compras',
    'Indicador de borrado',
    'Documento compras',
    'Grupo de compras',
    'Posición',
    'Cl.documento compras',
    'Por calcular (cantidad)',
    'Por entregar (valor)',
    'Fecha documento',
    'Proveedor/Centro suministrador',
    'Precio neto',
    'Moneda',
    'Texto breve',
    'Mes',
    'Año',
    'Periodo',
    'Tipo',
    'Área'
]
columns_int = [
    'Documento compras',
    'Grupo de compras',
    'Posición',
]
columns_float = [
    'Por calcular (cantidad)',
    'Por entregar (valor)',
    'Precio neto',
]   

all_columns = {
    'Columns':columns,
    'Columns Integer':columns_int,
    'Columns Float':columns_float,
}

#FORMULAS
formula_hes = '=IF({value}2=0,"HES 100%","PENDIENTE DE HES")'
formula_mes = '=MONTH({value}2)'
formula_año = '=YEAR({value}2)'
formula_periodo = '=CONCATENATE({value1}2,"-",{value2}2)'
formula_tipo = '''
=IF({value}2="ZSER","Servicios",
(IF({value}2="ZNAC","Materiales",
(IF({value}2="ZPRY","Proyectos",
IF({value}2="ZPAF","Activo Fijo",
IF({value}2="ZPCO","Costos",
"")))))))'''
formula_area = '''
=IF({value}2=1,"Adm y Finanzas",
IF({value}2=2,"Comercial",
IF({value}2=3,"Contabilidad",
IF({value}2=4,"Informática"
,IF({value}2=5,"Mantención"
,IF({value}2=6,"Operaciones"
,IF({value}2=7,"Personas"
,IF({value}2=8,"SSO"
,IF({value}2=9,"Proyectos"
,IF({value}2=10,"Medio Ambiente"
,IF({value}2=13,"Mecánica",
IF({value}2=14,"Electro-Control",
""))))))))))))'''

all_formulas = {
    'HES' : formula_hes,
    'Mes' : formula_mes,
    'Año' : formula_año,
    'Periodo' : formula_periodo,
    'Tipo' : formula_tipo,
    'Área' : formula_area,
}

#OTHER DICTIONARIES
target_formula = {
    'HES' : 'Por entregar (valor)',
    'Mes' : 'Fecha documento',
    'Año' : 'Fecha documento',
    'Periodo' : ('Mes', 'Año'),
    'Tipo' : 'Cl.documento compras',
    'Área' : 'Grupo de compras',
}

