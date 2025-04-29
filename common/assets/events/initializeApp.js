document.addEventListener("DOMContentLoaded", function () {
    // Inicializa QWebChannel una sola vez
    new QWebChannel(qt.webChannelTransport, function (channel) {
        console.log("QWebChannel inicializado");
        window.handler = channel.objects.handler;

        //Llama a las funciones de inicializacion
        initializerPages();
        initializerSidebar();
        initializerUploadFile();
        initializerCreateHesFile();
        initializerSendButtonStates();
        initializerCreateButtonStates();
        initializerCreatePymeFile();
        initializerTablePyme();
    });
});

