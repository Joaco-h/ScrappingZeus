# Zeus Scraper + CAPTCHA Solver :mortar_board:

Proyecto académico de automatización, web scraping y machine learning aplicado a la resolución de CAPTCHAs numéricos del portal Zeus del Servicio de Impuestos Internos (SII) de Chile.

Esta herramienta permite consultar información pública de RUTs en el portal Zeus, resolviendo automáticamente los CAPTCHAs mediante un modelo de IA entrenado con ejemplos reales.



## :rocket: Funcionalidades principales

Scraper automatizado que interactúa con la plataforma Zeus.

Modelo de Machine Learning capaz de resolver CAPTCHAs numéricos distorsionados.

Interfaz gráfica (opcional) para carga masiva de RUTs.

Módulo de integración directa para programadores que desean incorporar esta funcionalidad en sus propios proyectos.

Sistema de recolección de imágenes para seguir entrenando y mejorando el modelo.

## :hammer_and_wrench: Tecnologías utilizadas

Python 3

Selenium

TensorFlow / Keras

OpenCV

Pandas

Tkinter (para interfaz gráfica)

Pillow (PIL)



## :framed_picture: ¿Cómo son los CAPTCHAs del portal Zeus?

El portal utiliza CAPTCHAs que consisten en 4 dígitos numéricos, presentados con diferentes colores de fondo, distorsión de las cifras y líneas de ruido que atraviesan los números. Aunque son visualmente alterados, mantienen patrones consistentes que permiten su resolución mediante un modelo entrenado adecuadamente.



## :zap: Instalación y uso rápido




### Clona este repositorio
git clone https://github.com/TU_USUARIO/zeus-scraper-captcha-solver.git
### Entra en el proyecto
cd zeus-scraper-captcha-solver
### Instala las dependencias
pip install -r requirements.txt

### :fire: Para usar el objeto programático:
from zeus_scraper import Zeus
#### Lista de RUTs
ruts = ["12345678-9", "98765432-1"]
#### Crear objeto Zeus
zeus = Zeus(ruts=ruts)
#### Acceder a la información
print(zeus["12345678-9"].name)

### :desktop_computer: Para usar el front-end:

python frontend.py

Esto abrirá una ventana donde puedes cargar tu archivo de RUTs y descargar los resultados.

## :package: Descarga del modelo

Debido al tamaño del modelo de IA, no está directamente en el repositorio. Puedes descargarlo aquí:

➡ Descargar modelo entrenado desde Dropbox

(Recuerda mover el archivo descargado a la carpeta captcha_solver/ antes de ejecutar.)

## :warning: Importante

Este proyecto es exclusivamente académico.

Disclaimer: Debido a la naturaleza del portal Zeus, al consultar RUTs es posible obtener nombres asociados visibles públicamente. Se recomienda realizar un proceso de limpieza de los datos antes de cualquier uso adicional.

## :file_folder: Estructura del proyecto

zeus-scraper-captcha-solver/
├── captcha_collector/       # Scripts para recolectar y guardar imágenes de CAPTCHAs
├── captcha_solver/          # Entrenamiento del modelo IA
├── zeus_scraper/            # Scraper principal y clase Zeus
├── frontend/                # Interfaz gráfica
├── requirements.txt         # Librerías necesarias
├── README.md                # Este documento
├── LICENSE                  # Licencia MIT
└── .gitignore               # Ignorar archivos innecesarios

## :clapper: Video demostrativo

[Próximamente: Link al video]

## :handshake: Contribuciones

¡Toda ayuda es bienvenida!
Si quieres mejorar el proyecto o adaptarlo, siéntete libre de abrir un issue o enviar un pull request.

## :link: Contacto

[Tu perfil de LinkedIn] | [Tu correo o portfolio]

## :memo: Licencia

Este proyecto está licenciado bajo los términos de la Licencia MIT.

Se permite su uso, copia, modificación y distribución libremente, siempre bajo las condiciones indicadas.
Este software se proporciona "tal cual", sin garantía de ningún tipo.
El uso de esta herramienta es responsabilidad exclusiva del usuario.

