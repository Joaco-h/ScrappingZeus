function initializerPages() {
    loadDynamicContent('./features/dashboard/pages/page.html', []);
    
    document.getElementById('dashboard__page').addEventListener('click', function() {
        loadDynamicContent('./features/dashboard/pages/page.html', []);
    });

    document.getElementById('contact__page').addEventListener('click', function() {
        loadDynamicContent('./features/contact/pages/page.html', []);
    });
    
    document.getElementById('hes__page').addEventListener('click', function() {
        loadDynamicContent('./features/pendiente_hes/pages/page.html',
            [initializerCreateButtonStates, initializerSendButtonStates, initializerCreateHesFile, initializerUploadFile]);
    });
    
    document.getElementById('pyme__page').addEventListener('click', function() {
        loadDynamicContent('./features/pyme_finder/pages/page.html', 
            [initializerCreatePymeFile, initializerTablePyme]);
    });
    
}