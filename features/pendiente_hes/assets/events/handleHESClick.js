//Funcion de carga de archivos
function initializerUploadFile() {
    setupDragAndDrop("dropcontainer__actual", "file__actual");
    setupDragAndDrop("dropcontainer__previo", "file__previo");
}

//Funcion de creacion archivo Pendientes de HES
function initializerCreateHesFile () {
    //Evento de boton1
    const createHesFileBtn = document.getElementById("create_hes_file");
    if (createHesFileBtn) {
        createHesFileBtn.addEventListener("click", function () {
            console.log("Botón 'create_hes_file' presionado");
            handler.send_order_to_server("Crea el archivo Excel", [], function (response) {
                console.log("Respuesta del servidor", response);
                alert(response);
            });
        });
    } else {
        console.error("No se encontró el botón con ID 'create_hes_file'");
    }
    
    //Evento de boton2
    const splitHesFileBtn = document.getElementById("split_file");
    if (splitHesFileBtn) {
        splitHesFileBtn.addEventListener("click", function () {
            console.log("Botón 'split_file' presionado");
            handler.send_order_to_server("Divide el archivo", [], function (response) {
                console.log("Respuesta del servidor", response);
                alert("Respuesta del servidor", response);
            });
        });
    } else {
        console.log("No se econtró el botón con ID 'split_file'")
    }
    
    //Evento de boton3
    const sendEmailBtn = document.getElementById("send_email");
    if (sendEmailBtn) {
        sendEmailBtn.addEventListener("click" , function () {
            const valuesChecked = getCheckedValues("field__checkbox--hes")
            const valueDate = document.getElementById("dateinput__hes").value
            
            valuesChecked.unshift(valueDate)
            console.log("Botón 'send_email' presionado");
            handler.send_order_to_server("Envia el email", valuesChecked, function (response) {
                console.log("Respuesta del servidor", valuesChecked, response);
                alert(valuesChecked);
            });
        });
    } else {
        console.log("No se encontró el botón con ID 'send_email'")
    }
}
