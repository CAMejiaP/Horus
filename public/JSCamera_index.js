document.addEventListener('DOMContentLoaded', async () => {
    const video = document.getElementById('camera');
    const canvas = document.getElementById('canvas');
    const captureButton = document.getElementById('capture');
    const previewImage = document.getElementById('preview');
    const output = document.getElementById('output');
    const processButton = document.getElementById('processImage');

    // Acceder a la cámara del dispositivo
    try {
        const stream = await navigator.mediaDevices.getUserMedia({ video: { facingMode: "environment" } });
        video.srcObject = stream;
        await video.play();
    } catch (error) {
        console.error("Error al acceder a la cámara:", error);
        alert("No se pudo acceder a la cámara. Verifica los permisos.");
    }

    // Capturar la imagen de la cámara con un pequeño retraso para mejorar enfoque
    captureButton.addEventListener('click', async () => {
        previewImage.src = "";
        previewImage.style.display = 'none';

        await new Promise(resolve => setTimeout(resolve, 500)); // Espera 500ms para mejorar el enfoque

        const context = canvas.getContext('2d');
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
        context.drawImage(video, 0, 0, canvas.width, canvas.height);

        const imageURL = canvas.toDataURL('image/png'); // Mejor formato para OCR
        previewImage.src = imageURL;
        previewImage.style.display = 'block';
    });

    // Lista blanca de caracteres permitidos (Español + Braille Unicode)
    const whitelist = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyzÁÉÍÓÚÑáéíóúñ.,!?()0123456789" +
                      "⠁⠂⠃⠄⠅⠆⠇⠈⠉⠊⠋⠌⠍⠎⠏⠐⠑⠒⠓⠔⠕⠖⠗⠘⠙⠚⠛⠜⠝⠞⠟" +
                      "⠠⠡⠢⠣⠤⠥⠦⠧⠨⠩⠪⠫⠬⠭⠮⠯⠰⠱⠲⠳⠴⠵⠶⠷⠸⠹⠺⠻⠼⠽⠾⠿";

    // Función para mejorar la imagen antes del OCR (Escala de grises y umbralización)
    async function preprocessImageForOCR(imageElement) {
        const canvas = document.createElement('canvas');
        const ctx = canvas.getContext('2d');

        canvas.width = imageElement.width;
        canvas.height = imageElement.height;
        ctx.drawImage(imageElement, 0, 0, canvas.width, canvas.height);

        const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
        const data = imageData.data;

        // Convertir a escala de grises y aplicar umbralización adaptativa
        for (let i = 0; i < data.length; i += 4) {
            let gray = (data[i] + data[i + 1] + data[i + 2]) / 3;
            gray = gray > 150 ? 255 : 0; // Ajustar umbral para mejorar detección
            data[i] = data[i + 1] = data[i + 2] = gray;
        }

        ctx.putImageData(imageData, 0, 0);
        return canvas.toDataURL('image/png'); // Convertir a PNG (mejor para OCR)
    }

    // Procesar la imagen y detectar Braille o Texto en español
    processButton.addEventListener('click', async () => {
        if (!previewImage.src) {
            alert("Primero toma una foto.");
            return;
        }

        output.innerHTML = "Procesando imagen...";

        // Mejorar la imagen antes de OCR
        const processedImageSrc = await preprocessImageForOCR(previewImage);
        
        const img = document.createElement("img");
        img.src = processedImageSrc;
        img.style.display = "none";
        document.body.appendChild(img);

        img.onload = async () => {
            const { data: { text } } = await window.Tesseract.recognize(
                img.src,
                'spa',  // Solo idioma español
                {
                    logger: m => console.log(m),
                    tessedit_char_whitelist: whitelist, // Solo caracteres permitidos
                    preserve_interword_spaces: true,
                    oem: 1, // Mejor motor OCR
                    psm: 6  // Bloques de texto
                }
            );

            output.innerHTML = `<h3>Texto Detectado:</h3><p>${text.trim()}</p>`;
        };
    });
});
