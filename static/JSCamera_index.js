let globalOriginalImageData = null;
let outputField = null;

document.addEventListener('DOMContentLoaded', async () => {
    const folderButton = document.getElementById('folder');
    const fileInput = document.getElementById('fileInput');
    outputField = document.getElementById('inputText');
    const displayDiv = document.getElementById('Id_fileDisplay');
    const actual_language = document.getElementById('inputLanguage');
    let idiomaSeleccionado = "";

    const contrasteTemplate = `
    <div class="contenedor_contraste ui raised very padded segment" id="todo_contraste" style="display: block;">
        <div class="ui form">
            <div class="field">
                <label for="uploadImage" hidden>Subir imagen</label>
                <input type="file" id="uploadImage" accept="image/*" hidden>
            </div>            
        </div>
        <div class="ui divider"></div>
        <div class="ui two column grid">
            <div class="column">
                <h4 class="ui header">Imagen Original</h4>
                <canvas id="originalCanvas"></canvas>
            </div>
            <div class="field">
                <label for="contrastSlider">Contraste: <span id="contrastValue" class="ui label">0</span></label>
                <div class="range-wrapper">
                    <input id="contrastSlider" type="range" min="-100" max="100" value="0">
                </div>
            </div>
            <div class="column">
                <h4 class="ui header">Contraste Aplicado</h4>
                <canvas id="contrastCanvas"></canvas>
            </div>
        </div>
        <div class="ui divider"></div>
        <div style="text-align:center; margin-top: 1rem;">
            <button id="sendContrastBtn" class="ui primary button">Enviar</button>
        </div>
    </div>
    `;


    folderButton.addEventListener('click', () => {
        fileInput.click();
    });

    fileInput.addEventListener('change', async (event) => {
        const file = event.target.files[0];
        idiomaSeleccionado = actual_language.value;

        if (!file) return;

        if (idiomaSeleccionado === "espanol") {
            displayDiv.innerHTML = '';

            const menu_contraste = document.getElementById('todo_contraste');
            if (menu_contraste) menu_contraste.style.display = 'none';

            if (file.type.startsWith('image/')) {
                const reader = new FileReader();
                reader.onload = async function (e) {
                    const img = document.createElement('img');
                    img.src = e.target.result;
                    displayDiv.appendChild(img);

                    outputField.value = "Procesando imagen cargada...";
                    await sendToServer(e.target.result, file.name);
                };
                reader.readAsDataURL(file);
            } else if (file.type === 'application/pdf') {
                const objectURL = URL.createObjectURL(file);
                const pdfPreview = document.createElement('embed');
                pdfPreview.src = objectURL;
                pdfPreview.type = 'application/pdf';
                pdfPreview.width = '100%';
                pdfPreview.height = '300px';
                displayDiv.appendChild(pdfPreview);

                outputField.value = "Procesando PDF...";
                await sendToServer(objectURL, file.name);
            } else {
                alert('Solo se aceptan archivos JPG, PNG o PDF.');
            }

            fileInput.value = '';
        }

        else if (idiomaSeleccionado === "braille") {
            displayDiv.innerHTML = '';

            if (file.type.startsWith('image/')) {
                const viejoMenu = document.getElementById('todo_contraste');
                if (viejoMenu) viejoMenu.remove();

                displayDiv.insertAdjacentHTML('beforeend', contrasteTemplate);
                inicializarContraste();

                const reader = new FileReader();
                reader.onload = async function (e) {
                    const img = new Image();
                    img.onload = function () {
                        const canvas = document.getElementById('originalCanvas');
                        if (!canvas) {
                            console.error("❌ No se encontró el canvas 'originalCanvas'");
                            return;
                        }

                        const ctx = canvas.getContext('2d');
                        canvas.width = img.width;
                        canvas.height = img.height;
                        ctx.drawImage(img, 0, 0);

                        // ⚡ Aplicar contraste automáticamente
                        const originalImageData = ctx.getImageData(0, 0, img.width, img.height);
                        globalOriginalImageData = originalImageData;
                        aplicarContrasteDesdeImageData(originalImageData, img.width, img.height);
                    };
                    img.src = e.target.result;

                    outputField.value = "Para ver el resultado, ajuste el contraste y presione Enviar";
                    fileInput.value = '';
                };
                reader.readAsDataURL(file);
            }

            else if (file.type === 'application/pdf') {
                const objectURL = URL.createObjectURL(file);
                const pdfPreview = document.createElement('embed');
                pdfPreview.src = objectURL;
                pdfPreview.type = 'application/pdf';
                pdfPreview.width = '100%';
                pdfPreview.height = '300px';
                displayDiv.appendChild(pdfPreview);

                const menu_contraste = document.getElementById('todo_contraste');
                if (menu_contraste) menu_contraste.style.display = 'none';

                outputField.value = "Procesando PDF...";

                const reader = new FileReader();
                reader.onload = async function (e) {
                    const typedarray = new Uint8Array(e.target.result);
                    const pdf = await pdfjsLib.getDocument({ data: typedarray }).promise;
                    let text = '';

                    for (let i = 1; i <= pdf.numPages; i++) {
                        const page = await pdf.getPage(i);
                        const content = await page.getTextContent();
                        const pageText = content.items.map(item => item.str).join(' ');
                        text += pageText + '\n';
                    }

                    outputField.value = text;
                    fileInput.value = '';
                };
                reader.readAsArrayBuffer(file);
            }
        }
    });

    const downloadSignageBtn = document.getElementById('downloadSignageBtn');
    downloadSignageBtn.addEventListener('click', async () => {
        const outputText = document.getElementById('outputText').value;

        try {
            const response = await fetch('/download_pdf', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ text: outputText })
            });

            if (!response.ok) throw new Error('❌ Error al generar el PDF');

            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'traduccion.pdf';
            document.body.appendChild(a);
            a.click();
            a.remove();
            window.URL.revokeObjectURL(url);
        } catch (err) {
            console.error('⚠️ Error descargando el PDF:', err);
            alert('Hubo un problema al generar el PDF.');
        }
    });
});

// 🧠 Función para inicializar controles del menú de contraste
function inicializarContraste() {
    const upload = document.getElementById("uploadImage");
    const contrastSlider = document.getElementById("contrastSlider");
    const contrastValue = document.getElementById("contrastValue");
    const originalCanvas = document.getElementById("originalCanvas");
    const contrastCanvas = document.getElementById("contrastCanvas");

    globalOriginalImageData = null;

    if (!upload || !contrastSlider || !originalCanvas || !contrastCanvas) {
        console.warn("⛔ Elementos de contraste no encontrados.");
        return;
    }

    upload.addEventListener("change", (e) => {
        const file = e.target.files[0];
        const reader = new FileReader();
        reader.onload = (event) => {
            const img = new Image();
            img.onload = () => {
                originalCanvas.width = img.width;
                originalCanvas.height = img.height;
                contrastCanvas.width = img.width;
                contrastCanvas.height = img.height;

                const ctx = originalCanvas.getContext("2d");
                ctx.drawImage(img, 0, 0);
                globalOriginalImageData = ctx.getImageData(0, 0, img.width, img.height);
                applyContrast();
            };
            img.src = event.target.result;
        };
        reader.readAsDataURL(file);
    });

    contrastSlider.addEventListener("input", () => {
        contrastValue.textContent = contrastSlider.value;
        applyContrast();
    });

    function applyContrast() {
        if (!globalOriginalImageData) return;

        const contrast = parseInt(contrastSlider.value);
        const brightness = 70;
        const factor = (259 * (contrast + 255)) / (255 * (259 - contrast));

        const ctx = contrastCanvas.getContext("2d");
        const data = new Uint8ClampedArray(globalOriginalImageData.data);

        for (let i = 0; i < data.length; i += 4) {
            data[i] = truncate(factor * (data[i] - 128) + 128 + brightness);
            data[i + 1] = truncate(factor * (data[i + 1] - 128) + 128 + brightness);
            data[i + 2] = truncate(factor * (data[i + 2] - 128) + 128 + brightness);
        }

        const imageData = new ImageData(data, globalOriginalImageData.width, globalOriginalImageData.height);
        ctx.putImageData(imageData, 0, 0);
    }
    const sendBtn = document.getElementById('sendContrastBtn');
    sendBtn.addEventListener('click', async () => {
        const originalCanvas = document.getElementById('originalCanvas');
        const contrastCanvas = document.getElementById('contrastCanvas');

        if (!originalCanvas || !contrastCanvas) {
            alert("No se encontraron los canvases.");
            return;
        }

        // Convertir ambos canvases a Base64
        const originalBase64 = originalCanvas.toDataURL('image/png');
        const contrastBase64 = contrastCanvas.toDataURL('image/png');

        outputField.value = "Enviando imágenes al servidor...";

        try {
            const response = await fetch('/getbraille', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    image: originalBase64,
                    contrast_image: contrastBase64,
                    filename: 'imagen_braille.png'
                })
            });

            const result = await response.json();
            outputField.value = result.text || "No se pudo extraer texto.";

            // Mostrar la imagen procesada en #Id_fileDisplay
            const displayDiv = document.getElementById('Id_fileDisplay');
            if (displayDiv && result.image) {
                displayDiv.innerHTML = ''; // Limpiar antes
                const resultImg = new Image();
                resultImg.src = result.image;
                resultImg.alt = "Resultado procesado";
                resultImg.style.maxWidth = "100%";
                resultImg.style.marginTop = "1rem";
                displayDiv.appendChild(resultImg);
            }


        } catch (error) {
            outputField.value = "Error al enviar imágenes al servidor.";
            console.error(error);
        }
    });

}

// 🎨 Contraste automático para fileInput
function aplicarContrasteDesdeImageData(originalImageData, width, height) {
    const contrastSlider = document.getElementById("contrastSlider");
    const contrastValue = document.getElementById("contrastValue");
    const contrastCanvas = document.getElementById("contrastCanvas");

    if (!contrastSlider || !contrastCanvas || !contrastValue) return;

    contrastSlider.value = 0;
    contrastValue.textContent = '0';

    const brightness = 70;
    const contrast = parseInt(contrastSlider.value);
    const factor = (259 * (contrast + 255)) / (255 * (259 - contrast));
    const data = new Uint8ClampedArray(originalImageData.data);

    for (let i = 0; i < data.length; i += 4) {
        data[i] = truncate(factor * (data[i] - 128) + 128 + brightness);
        data[i + 1] = truncate(factor * (data[i + 1] - 128) + 128 + brightness);
        data[i + 2] = truncate(factor * (data[i + 2] - 128) + 128 + brightness);
    }

    const ctx = contrastCanvas.getContext("2d");
    const imageData = new ImageData(data, width, height);
    contrastCanvas.width = width;
    contrastCanvas.height = height;
    ctx.putImageData(imageData, 0, 0);
}

// 🔧 Utilidad
function truncate(value) {
    return Math.max(0, Math.min(255, value));
}

// 📤 Envío al backend
async function sendToServer(imageData) {
    try {
        const blob = await fetch(imageData).then(res => res.blob());
        const formData = new FormData();
        formData.append('image', blob, 'captured.jpg');

        const response = await fetch('/upload', {
            method: 'POST',
            body: formData
        });

        const data = await response.json();
        outputField.value = data.text || 'No se detectó texto.';
    } catch (error) {
        outputField.value = 'Error procesando la imagen.';
    }
}

async function sendToParser(base64Image, filename) {
    try {
        const response = await fetch('/getbraille', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ image: base64Image, filename })
        });

        const result = await response.json();
        outputField.value = result.text || "No se pudo extraer texto.";
    } catch (error) {
        outputField.value = "Error al procesar imagen.";
    }
}
