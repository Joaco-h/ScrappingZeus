function initializerCreatePymeFile () {
    const createPymeFileBtn = document.getElementById("predict_captcha");

    if (createPymeFileBtn) {
        createPymeFileBtn.addEventListener("click", function () {
            console.log("Botón 'predict_captcha' presionado");
            
            handler.send_order_to_server("Predice el Captcha", [], function (response) {
                console.log("Respuesta del servidor", response);
                alert(response);
                
                // Pedimos la imagen luego de un breve retardo
                setTimeout(mostrarImagen, 7000);  // espera 1 segundo por si aún no termina
            });
        });
    } else {
        console.error("No se encontró el botón con ID 'predict_captcha'");
    }
}

function mostrarImagen () {
    handler.get_image_base64().then(function (base64Data) {
        if (!base64Data || base64Data.length < 10) {
            console.warn("Imagen aún no disponible.");
            return;
        }
        const imgElement = document.getElementById('dynamic-image');
        imgElement.src = "data:image/png;base64," + base64Data;

        // También obtenemos la predicción
        handler.get_captcha_prediction().then(function (prediccion) {
            const predSpan = document.getElementById("prediction_text");
            predSpan.textContent = prediccion || "Sin predicción";
        });
    });
}

