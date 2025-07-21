function initializerCreatePymeFile () {
    const createPymeFileBtn = document.getElementById("create_pyme_file");
    const fileInput = document.getElementById("fileInputPyme")
    
    if (createPymeFileBtn) {
        createPymeFileBtn.addEventListener("click", function () {
                if (cellAddresses.rutPyme && cellAddresses.lastRowPyme) {
                    console.log('Contenido de cellAddresses:', JSON.stringify(cellAddresses, null, 2));
                    console.log("Botón 'create_pyme_file' presionado");
                    handler.send_order_to_server("Crea el archivo Pyme", [cellAddresses], function (response) {
                        console.log("Respuesta del servidor", response);
                        alert(response);
                    });
                } else {
                    alert('Por favor, selecciona todas las celdas requeridas.');
                };
        });
    } else {
        console.error("No se encontró el botón con ID 'create_pyme_file'");
    }

    if (fileInput) {
        fileInput.addEventListener("change", function () {
            uploadFile(fileInput.files[0], "fileInputPyme");
        });
    } else {
        console.log("No se encontró el archivo con ID 'fileInputPyme'")
    }
}

let selectedCell = null;
let cellAddresses = { rutPyme: null, namePyme: null, lastRowPyme: null, sheetname: null, wbname: null };

function initializerTablePyme () {
    document.getElementById('fileInputPyme').addEventListener('change', handleFileChange);
    document.getElementById('sheetSelector').addEventListener('change', handleSheetChange);
    document.getElementById('findRutPyme').addEventListener('click', () => assignCell('rutPyme'));
    document.getElementById('findNamePyme').addEventListener('click', () => assignCell('namePyme'));
    document.getElementById('findLastRowPyme').addEventListener('click', () => assignCell('lastRowPyme'));

}
