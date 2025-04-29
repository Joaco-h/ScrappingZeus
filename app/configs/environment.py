import sys
import os
from pathlib import Path

class Environment:
    """Clase para manejar la configuración del entorno de la aplicación."""
    
    def __init__(self):
        self.project_root = self._setup_project_root()
        self.setup_python_path()
        self.setup_directories()
    
    def _setup_project_root(self) -> Path:
        """Configura y retorna la ruta raíz del proyecto."""
        return Path(__file__).parent.parent.parent
    
    def setup_python_path(self):
        """Configura el PYTHONPATH."""
        project_root_str = str(self.project_root)
        if project_root_str not in sys.path:
            sys.path.append(project_root_str)
    
    def setup_directories(self):
        """Configura las rutas de directorios importantes."""
        self.templates_dir = self.project_root / "templates"
        self.static_dir = self.project_root / "static"
        self.data_dir = self.project_root / "data"
        
        # Crear directorios si no existen
        for directory in [self.templates_dir, self.static_dir, self.data_dir]:
            directory.mkdir(exist_ok=True)
    
    @property
    def debug_mode(self) -> bool:
        """Determina si la aplicación está en modo debug."""
        return os.getenv('DEBUG', 'False').lower() == 'true'

# Crear una instancia global de Environment
env = Environment()

# Exportar variables comúnmente usadas
PROJECT_ROOT = env.project_root
TEMPLATES_DIR = env.templates_dir
STATIC_DIR = env.static_dir
DATA_DIR = env.data_dir
DEBUG = env.debug_mode 