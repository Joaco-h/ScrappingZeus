document.addEventListener('DOMContentLoaded', function() {
    // Navegación entre páginas
    const navLinks = document.querySelectorAll('.nav-link');
    const pages = document.querySelectorAll('.page');

    navLinks.forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            const targetPage = link.getAttribute('data-page');

            // Actualizar navegación
            navLinks.forEach(l => l.classList.remove('active'));
            link.classList.add('active');

            // Mostrar página correspondiente
            pages.forEach(page => {
                if (page.id === targetPage) {
                    page.classList.add('active');
                } else {
                    page.classList.remove('active');
                }
            });
        });
    });

    // Manejo del formulario de extracción de captchas
    const captchaForm = document.getElementById('captcha-form');
    if (captchaForm) {
        captchaForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const count = document.getElementById('captcha-count').value;
            
            // Comunicación con PySide6
            window.pyside.extractCaptchas(count);
        });
    }

    // Manejo de carga de archivo y visualización de RUTs
    const loadFileBtn = document.getElementById('load-file');
    const rutContainer = document.getElementById('rut-container');
    
    if (loadFileBtn) {
        loadFileBtn.addEventListener('click', () => {
            // Comunicación con PySide6 para abrir diálogo de archivo
            window.pyside.openFileDialog();
        });
    }

    // Función para mostrar los RUTs en el contenedor
    window.displayRuts = function(ruts) {
        if (!rutContainer) return;
        
        rutContainer.innerHTML = '';
        ruts.forEach(rut => {
            const rutItem = document.createElement('div');
            rutItem.className = 'rut-item';
            rutItem.innerHTML = `
                <span>${rut}</span>
                <i class="fas fa-check"></i>
            `;
            rutContainer.appendChild(rutItem);
        });
    }

    // Manejo del inicio del scraping
    const startScrapingBtn = document.getElementById('start-scraping');
    if (startScrapingBtn) {
        startScrapingBtn.addEventListener('click', () => {
            // Comunicación con PySide6
            window.pyside.startScraping();
        });
    }
}); 