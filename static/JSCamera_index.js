document.addEventListener('DOMContentLoaded', async () => {
    const video = document.getElementById('cameraView');
    const captureButton = document.getElementById('camera');
    const folderButton = document.getElementById('folder');
    const fileInput = document.getElementById('fileInput');
    const outputField = document.getElementById('inputText');
    const displayDiv = document.getElementById('Id_fileDisplay');
    const canvas = document.getElementById('canvas');
    const context = canvas.getContext('2d');

    async function startCamera() {
        try {
            const constraints = { video: { facingMode: 'environment' } };
            const stream = await navigator.mediaDevices.getUserMedia(constraints);
            video.srcObject = stream;
        } catch (error) {
            console.error('🚨 Error al acceder a la cámara:', error);
            alert('No se pudo acceder a la cámara. Verifica los permisos.');
        }
    }

    folderButton.addEventListener('click', () => {
        fileInput.click();
    });

    captureButton.addEventListener('click', async () => {
        if (!video.srcObject) await startCamera();

        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
        context.drawImage(video, 0, 0, canvas.width, canvas.height);

        const imgData = canvas.toDataURL('image/jpeg');
        const img = document.createElement('img');
        img.src = imgData;
        displayDiv.innerHTML = '';
        displayDiv.appendChild(img);

        stopCamera();

        outputField.value = "Procesando imagen capturada...";
        await sendToServer(imgData);
    });

    fileInput.addEventListener('change', async (event) => {
    const file = event.target.files[0];
    if (file) {
        const reader = new FileReader();
        reader.onload = async function (e) {
            const img = document.createElement('img');
            img.src = e.target.result;
            displayDiv.innerHTML = '';
            displayDiv.appendChild(img);
            stopCamera();

            outputField.value = "Procesando imagen cargada...";
            await sendToServer(e.target.result);

            // 🔁 Limpiar input file para poder seleccionar la misma imagen de nuevo si se desea
            fileInput.value = '';
        };
        reader.readAsDataURL(file);
    }
});


    async function sendToServer(imageData) {
        try {
            const blob = await fetch(imageData).then(res => res.blob());
            const formData = new FormData();
            formData.append('image', blob, 'captured.jpg');

            console.log("📤 Enviando imagen al servidor...");
            const response = await fetch('http://127.0.0.1:5000/upload', {
                method: 'POST',
                body: formData
            });

            if (!response.ok) throw new Error(`⚠️ Error en el servidor: ${response.status}`);
            const data = await response.json();
            console.log(`✅ Respuesta del servidor: ${data.text}`);

            outputField.value = data.text || 'No se detectó texto.';
        } catch (error) {
            console.error('🚨 Error procesando la imagen:', error);
            outputField.value = 'Error procesando la imagen.';
        }
    }

    function stopCamera() {
        const stream = video.srcObject;
        if (stream) {
            stream.getTracks().forEach(track => track.stop());
            video.srcObject = null;
        }
    }

    startCamera();

    // 🔽 Descargar PDF normal
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
            a.download = 'traduccion_braille.pdf';
            document.body.appendChild(a);
            a.click();
            a.remove();
            window.URL.revokeObjectURL(url);
        } catch (err) {
            console.error('⚠️ Error descargando el PDF:', err);
            alert('Hubo un problema al generar el PDF.');
        }
    });

    // 🔽 Descargar PDF en espejo
    const downloadMirrorImageBtn = document.getElementById('downloadMirrorImageBtn');
    downloadMirrorImageBtn.addEventListener('click', async () => {
        const outputText = document.getElementById('outputText').value;

        try {
            const response = await fetch('/download_pdf_mirror', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ text: outputText })
            });

            if (!response.ok) throw new Error('❌ Error al generar el PDF en espejo');

            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'traduccion_braille_espejo.pdf';
            document.body.appendChild(a);
            a.click();
            a.remove();
            window.URL.revokeObjectURL(url);
        } catch (err) {
            console.error('⚠️ Error descargando el PDF espejo:', err);
            alert('Hubo un problema al generar el PDF espejo.');
        }
    });
});
