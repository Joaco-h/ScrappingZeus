function uploadFile(file, inputId) {
    const reader = new FileReader();
    
    reader.onload = function (e) {
        const fileContent = new Uint8Array(e.target.result);
        const fileName = file.name;
        
        console.log(`Contenido del archivo (${fileName}):`, fileContent);
        
        // Convert Uint8Array to a regular array
        const fileContentArray = Array.from(fileContent);
        
        // Send the file to the backend using QWebChannel, including the input ID
        handler.send_file_to_backend(fileName, inputId, fileContentArray, function (response) {
            alert(`Respuesta del backend: ${response}`);
        });
    };
    
    reader.onerror = function (e) {
        console.error("Error al leer el archivo:", e);
    };
    
    reader.readAsArrayBuffer(file); // Read as ArrayBuffer for binary files
}

function setupDragAndDrop(dropContainerId, fileInputId) {
    const dropContainer = document.getElementById(dropContainerId);
    const fileInput = document.getElementById(fileInputId);
    
    //Realizar accion al soltar el archivo sobre el contenedor
    dropContainer.addEventListener('dragover', (e) => {
        e.preventDefault();
    }, false);
    
    dropContainer.addEventListener('dragenter', () => {
        dropContainer.classList.add('drag-active');
    });
    
    dropContainer.addEventListener('dragleave', () => {
        dropContainer.classList.remove('drag-active');
    });
    
    dropContainer.addEventListener('drop', (e) => {
        e.preventDefault();
        dropContainer.classList.remove('drag-active');
        fileInput.files = e.dataTransfer.files;
        
        const uploadedFile = fileInput.files[0];
        if (uploadedFile) {
            console.log(`Archivo subido desde ${fileInputId}: ${uploadedFile.name}`);
            uploadFile(uploadedFile, fileInputId); // Pass the input ID to the backend
        }
    });
    
    //Realizar accion al seleccionar el archivo desde el selector
    fileInput.addEventListener("change", (e) => {
        const uploadedFile = fileInput.files[0];
        if (uploadedFile) {
            console.log(`Archivo seleccionado desde ${fileInputId}: ${uploadedFile.name}`);
            uploadFile(uploadedFile, fileInputId) // Pass the input ID to the backend
        }
    });
}

function handleDrop(event, fileInput, selectors, buttonsList) {
    event.preventDefault();
    event.stopPropagation();

    console.log("✅ Evento drop detectado");

    const files = event.dataTransfer.files;
    console.log("📂 Archivos arrastrados:", files.length);

    if (files.length > 0) {
        const dataTransfer = new DataTransfer();
        for (let i = 0; i < files.length; i++) {
            dataTransfer.items.add(files[i]);
        }
        fileInput.files = dataTransfer.files;

        console.log(`✅ Archivos asignados correctamente a ${fileInput.id}:`, fileInput.files.length);
    }

    checkFiles(selectors, buttonsList);
}

function handleDragOver(event) {
    event.preventDefault();
    event.stopPropagation();
    event.dataTransfer.dropEffect = "copy"; // Asegura que el cursor muestre la acción de copiar
}

function checkFiles(selectors, buttonsList) {
    console.log("Verificando archivos...");

    const filesSelected = selectors.every(selector => selector.files.length > 0);
    
    console.log("¿Archivos seleccionados?", filesSelected);

    buttonsList.forEach(({ button, overlay }) => {
        button.disabled = !filesSelected;
        overlay.style.display = button.disabled ? 'block' : 'none';
    });
}

function getCheckedValues (checkboxClass) {
    const checkListValues = document.getElementsByClassName(checkboxClass);
    const checkedValues = [];
    
    for (let i=0; i < checkListValues.length; i++) {
        if (checkListValues[i].checked) {
            checkedValues.push(checkListValues[i].value);
        }
    }
    return checkedValues
}

function loadDynamicContent(page, initFunctions) {
    fetch(page)
        .then(response => {
            if (!response.ok) {
                throw new Error('Fallo la conexion');
            }
            return response.text();
        })
        .then(data => {
            document.getElementById('content').innerHTML = data;
            if (initFunctions.length > 0) {
                initFunctions.forEach(func => func());
            }
        })
        .catch(error => {
            console.error('Error al cargar la página:', error);
            document.getElementById('content').innerHTML = '<p>Error al cargar la página. Por favor, inténtelo de nuevo más tarde.</p>';
        });
}

function assignCell(type) {
    if (selectedCell) {
        const cellAddress = selectedCell.getAttribute('data-cell-address');
        const prevCellAddress = cellAddresses[type];
        
        // Asignar la nueva celda
        cellAddresses[type] = cellAddress;
        selectedCell.style.backgroundColor = 'orange';
        document.querySelector(`#${type} .cell-address`).textContent = cellAddress;

        // Verificar si la celda anterior está asignada a otro botón
        if (prevCellAddress && !Object.values(cellAddresses).includes(prevCellAddress)) {
            const prevCell = document.querySelector(`[data-cell-address="${prevCellAddress}"]`);
            if (prevCell) {
                prevCell.style.backgroundColor = '';
            }
        }

        // Restablecer la celda seleccionada a null
        selectedCell = null;
    } else {
        alert('Por favor, selecciona una celda primero.');
    }
}

function resetAssignedCells() {
    for (let key in cellAddresses) {
        if (cellAddresses[key] && key !== 'sheetname' && key !== 'wbname') {
            const cell = document.querySelector(`[data-cell-address="${cellAddresses[key]}"]`);
            if (cell) {
                cell.style.backgroundColor = '';
            }
            cellAddresses[key] = null;
            document.querySelector(`#${key} .cell-address`).textContent = ''; // Limpiar el valor mostrado
        }
    }
}

function handleSheetChange(event) {
    resetAssignedCells(); // Resetear celdas asignadas y valores mostrados
    const sheetName = event.target ? event.target.value : event;
    console.log(`Sheet selected: ${sheetName}`); // Debugging line

    if (!window.workbookGlobal) {
        console.error("No hay un archivo cargado en memoria.");
        return;
    }

    if (!workbookGlobal.Sheets[sheetName]) {
        console.error(`La hoja "${sheetName}" no existe en el archivo.`);
        return;
    }

    displaySheet(workbookGlobal.Sheets[sheetName]);
    cellAddresses["sheetname"] = sheetName;
    console.log(`Sheet name set in cellAddresses: ${cellAddresses["sheetname"]}`);
}

function handleFileChange(event) {
    resetAssignedCells(); // Resetear celdas asignadas y valores mostrados
    const file = event.target.files[0];
    const reader = new FileReader();
    reader.onload = function(e) {
        const data = new Uint8Array(e.target.result);
        const workbook = XLSX.read(data, { type: 'array' });

        const nonEmptySheets = [];
        const emptySheets = [];
        
        // Validate empty sheets and non empty sheets
        workbook.SheetNames.forEach(sheetName => {
            const sheet = workbook.Sheets[sheetName];
            const isEmpty = !sheet['!ref'];
            if (isEmpty) {
                emptySheets.push(sheetName);
            } else {
                nonEmptySheets.push(sheetName);
            }
        });

        if (nonEmptySheets.length === 0) {
            console.error("No hay hojas con datos en el archivo.");
            return;
        }

        const firstSheetName = nonEmptySheets[0];
        displaySheet(workbook.Sheets[firstSheetName]);
        cellAddresses['sheetname'] = firstSheetName;
        cellAddresses['wbname'] = file.name;
        console.log(`Sheet name set in cellAddresses: ${cellAddresses['sheetname']}`); // Debugging line
        console.log(`Workbook name set in cellAddresses: ${cellAddresses['wbname']}`); // Debugging line
        
        //Save workbook on global variable
        window.workbookGlobal = workbook;
        
        // Populate sheet selector with sheet names
        const sheetSelector = document.getElementById('sheetSelector');
        sheetSelector.innerHTML = '';
        nonEmptySheets.forEach(sheetName => {
            const option = document.createElement('option');
            option.value = sheetName;
            option.textContent = sheetName;
            sheetSelector.appendChild(option);
        });

        // Set the first sheet as selected
        sheetSelector.value = firstSheetName;
        
        // Alert with empty sheets
        if (emptySheets.length > 0) {
            alert(`Las siguientes hojas están vacías y no se mostrarán: ${emptySheets.join(', ')}`);
        }
    };
    reader.readAsArrayBuffer(file);
}

function displaySheet(sheet) {
    const sheetContent = document.getElementById('excelTable');
    sheetContent.innerHTML = '';

    const range = XLSX.utils.decode_range(sheet['!ref']);
    const table = document.createElement('table');

    for (let rowNum = range.s.r; rowNum <= range.e.r; rowNum++) {
        const row = document.createElement('tr');
        for (let colNum = range.s.c; colNum <= range.e.c; colNum++) {
            const cellAddress = XLSX.utils.encode_cell({ r: rowNum, c: colNum });
            const cell = sheet[cellAddress];
            const cellElement = document.createElement('td');
            cellElement.setAttribute('data-cell-address', cellAddress);

            if (cell) {
                cellElement.textContent = cell.v;
            } else {
                cellElement.textContent = ''; // Celdas vacías
            }

            // Resaltar celdas asignadas
            if (Object.values(cellAddresses).includes(cellAddress)) {
                cellElement.style.backgroundColor = 'orange';
            }

            cellElement.addEventListener('click', () => {
                if (selectedCell) {
                    selectedCell.style.backgroundColor = '';
                    // Resaltar celdas asignadas nuevamente
                    if (Object.values(cellAddresses).includes(selectedCell.getAttribute('data-cell-address'))) {
                        selectedCell.style.backgroundColor = 'orange';
                    }
                }
                selectedCell = cellElement;
                cellElement.style.backgroundColor = 'yellow';
            });

            row.appendChild(cellElement);
        }
        table.appendChild(row);
    }

    sheetContent.appendChild(table);
}

function showFileonTable(event) {
    const file = event.target.files[0];
    const reader = new FileReader();
    reader.onload = function(e) {
        const data = new Uint8Array(e.target.result);
        const workbook = XLSX.read(data, { type: 'array' });
        const sheetNames = workbook.SheetNames;
        const sheetSelector = document.getElementById('sheetSelector');
        sheetSelector.innerHTML = '';
        sheetNames.forEach(sheetName => {
            const option = document.createElement('option');
            option.value = sheetName;
            option.text = sheetName;
            sheetSelector.appendChild(option);
        });
        displaySheet(workbook.Sheets[sheetNames[0]]);
    };
    reader.readAsArrayBuffer(file);
}