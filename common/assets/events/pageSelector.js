function initializerPages() {
    loadDynamicContent('./features/contact/pages/page.html', []);
    
    document.getElementById('contact__page').addEventListener('click', function() {
        loadDynamicContent('./features/contact/pages/page.html',
            []);
    });
    
    document.getElementById('zeus__page').addEventListener('click', function() {
        loadDynamicContent('./features/zeus/pages/page.html',
            []);
    });
    
    document.getElementById('captcha__page').addEventListener('click', function() {
        loadDynamicContent('./features/captcha/pages/page.html', 
            []);
    });
    
}