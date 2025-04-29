function initializerCreateButtonStates() {
    const fileSelector1 = document.getElementById("file__actual");
    const fileSelector2 = document.getElementById("file__previo");
    const fileSelectors = [fileSelector1, fileSelector2];

    const dropContainer1 = document.getElementById("dropcontainer__actual");
    const dropContainer2 = document.getElementById("dropcontainer__previo");
    const dropContainers = [dropContainer1, dropContainer2];

    const buttons = [
        { button: document.getElementById("create_hes_file"), overlay: document.querySelector("#create_hes_file_container .button-overlay") },
    ];

    // Inicializa el estado de los botones
    checkFiles(fileSelectors, buttons);

    // Eventos para selección manual de archivos
    fileSelectors.forEach(selector => {
        selector.addEventListener("change", () => checkFiles(fileSelectors, buttons));
    });

    // Eventos para arrastrar y soltar archivos en los contenedores
    dropContainers.forEach((container, index) => {
        container.addEventListener("dragover", handleDragOver);
        container.addEventListener("drop", (event) => handleDrop(event, fileSelectors[index], fileSelectors, buttons));
    });
}


function initializerSendButtonStates() {
    const date = document.getElementById("dateinput__hes");
    const checkboxes = document.querySelectorAll(".checklist__hes .field__checkbox--hes");
    
    const buttons = [
        { button: document.getElementById("send_email"), overlay: document.querySelector("#send_email_container .button-overlay") }
    ];
    
    function checkCheckBoxes() {
        const anySelected = Array.from(checkboxes).some(checkbox => checkbox.checked);
        const dateEntered = date?.value?.trim() !== "";
        
        buttons.forEach(({ button, overlay }) => {
            button.disabled = !(anySelected && dateEntered);
            overlay.style.display = button.disabled ? 'block' : 'none';
        });
    }
    
    checkCheckBoxes();
    
    checkboxes.forEach(checkbox => {
        checkbox.addEventListener("change", checkCheckBoxes);
    });

    date?.addEventListener("input", checkCheckBoxes);
    
    buttons.forEach(({ button, overlay }) => {
        overlay.addEventListener("click", (event) => {
            if (button.disabled) {
                event.preventDefault();
                if (!date.value.trim() && !Array.from(checkboxes).some(checkbox => checkbox.checked)) {
                    showCustomAlert("Debe ingresar una fecha y seleccionar un área para enviar los correos.");
                } else if (!date.value.trim()) {
                    showCustomAlert("Debe ingresar una fecha para enviar los correos.");
                } else {
                    showCustomAlert("Debe seleccionar un área para enviar los correos.");
                }
            }
        });
    });
}

function showCustomAlert(message) {
    const alertBox = document.getElementById("customAlert");
    const alertMessage = document.getElementById("customAlertMessage");
    alertMessage.textContent = message;
    alertBox.style.display = 'block'
    alertBox.classList.add('show');
    setTimeout(() => {
        alertBox.classList.remove('show');
        setTimeout(() => {
            alertBox.style.display = 'none';
        }, 500);
    }, 6000); // 3000 milisegundos = 3 segundos
}
