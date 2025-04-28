Zeus Scraper + CAPTCHA Solver 🎓🇨🇱
Proyecto académico de automatización, web scraping y machine learning aplicado a la resolución de CAPTCHAs numéricos del portal Zeus del Servicio de Impuestos Internos (SII) de Chile.

Esta herramienta permite consultar información pública de RUTs en el portal Zeus, resolviendo automáticamente los CAPTCHAs mediante un modelo de IA entrenado con ejemplos reales.

🚀 Funcionalidades principales
Scraper automatizado que interactúa con la plataforma Zeus.

Modelo de Machine Learning capaz de resolver CAPTCHAs numéricos distorsionados.

Interfaz gráfica (opcional) para carga masiva de RUTs.

Módulo de integración directa para programadores que desean incorporar esta funcionalidad en sus propios proyectos.

Sistema de recolección de imágenes para seguir entrenando y mejorando el modelo.

🛠️ Tecnologías utilizadas
Python 3

Selenium

TensorFlow / Keras

OpenCV

Pandas

Tkinter (para interfaz gráfica)

Pillow (PIL)

🖼️ ¿Cómo son los CAPTCHAs del portal Zeus?
El portal utiliza CAPTCHAs de 4 dígitos numéricos, con diferentes niveles de distorsión, fondos de colores variables y líneas de ruido que dificultan su lectura automatizada.

Aun así, los patrones son reconocibles, y un modelo bien entrenado puede superar estas dificultades con alta precisión.

⚡ Instalación y uso rápido
bash
Copiar
Editar
# Clona este repositorio
git clone https://github.com/TU_USUARIO/zeus-scraper-captcha-solver.git

# Entra en el proyecto
cd zeus-scraper-captcha-solver

# Instala las dependencias
pip install -r requirements.txt
🔥 Para usar el objeto programático:
python
Copiar
Editar
from zeus_scraper import Zeus

# Lista de RUTs
ruts = ["12345678-9", "98765432-1"]

# Crear objeto Zeus
zeus = Zeus(ruts=ruts)

# Acceder a la información
print(zeus["12345678-9"].name)
🖥️ Para usar el front-end:
bash
Copiar
Editar
python frontend.py
Esto abrirá una ventana donde puedes cargar tu archivo de RUTs y descargar los resultados.

⚠️ Importante
Este proyecto es exclusivamente académico.

Disclaimer: Debido a la naturaleza del portal Zeus, al consultar RUTs es posible obtener nombres asociados visibles públicamente. Se recomienda realizar un proceso de limpieza de los datos antes de cualquier uso adicional.

📂 Estructura del proyecto
bash
Copiar
Editar
zeus-scraper-captcha-solver/
├── captcha_collector/       # Scripts para recolectar y guardar imágenes de CAPTCHAs
│   ├── collect_captchas.py
│   ├── README.md
│
├── captcha_solver/          # Entrenamiento del modelo IA
│   ├── train_model.py
│   ├── model.h5             # Modelo entrenado (no subir pesado a GitHub; sugerir enlace de descarga)
│   ├── README.md
│
├── zeus_scraper/            # Scraper principal y clase Zeus
│   ├── zeus_scraper.py
│   ├── __init__.py
│   ├── README.md
│
├── frontend/                # Interfaz gráfica
│   ├── frontend.py
│   ├── README.md
│
├── requirements.txt         # Librerías necesarias
├── README.md                 # Este documento
├── LICENSE                   # (Opcional) Licencia del proyecto
└── .gitignore                # Para ignorar carpetas de modelos o datasets pesados
📹 Video demostrativo
[Coloca aquí el link al video en YouTube o Loom 🔗]

📈 Estado del proyecto
✅ Recolección de datos
✅ Entrenamiento del modelo
✅ Scraper funcional
✅ Front-End funcional
🔜 Mejoras en la precisión del modelo para futuros cambios de CAPTCHA

🤝 Contribuciones
¡Toda ayuda es bienvenida!
Si quieres mejorar el proyecto o adaptarlo, siéntete libre de abrir un issue o enviar un pull request.

🔗 Contacto
[Tu perfil de LinkedIn] | [Tu correo o portfolio]

Tags
#Python #MachineLearning #WebScraping #Selenium #InteligenciaArtificial #DataEngineering #Automatización #OpenSource #ProyectoAcadémico
