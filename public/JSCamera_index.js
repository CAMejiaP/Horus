document.addEventListener('DOMContentLoaded', async () => {
    const video = document.getElementById('cameraView');
    const captureButton = document.getElementById('camera');
    const folderButton = document.getElementById('folder'); // 🔹 Nuevo botón para seleccionar imagen
    const fileInput = document.getElementById('fileInput');
    const translateButton = document.getElementById('btntraducir');
    const outputField = document.getElementById('atraducir');
    const displayDiv = document.getElementById('Id_fileDisplay');
    const canvas = document.getElementById('canvas');
    const context = canvas.getContext('2d');

    async function startCamera() {
        try {
            const constraints = {
                video: { facingMode: 'environment' }
            };
            const stream = await navigator.mediaDevices.getUserMedia(constraints);
            video.srcObject = stream;
        } catch (error) {
            console.error('🚨 Error al acceder a la cámara:', error);
            alert('No se pudo acceder a la cámara. Verifica los permisos.');
        }
    }

    // 🔹 Permitir seleccionar imagen haciendo clic en la imagen de la carpeta
    folderButton.addEventListener('click', () => {
        fileInput.click(); // Simula un clic en el input de archivos
    });

    captureButton.addEventListener('click', async () => {
        if (!video.srcObject) {
            await startCamera();
        }
        
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
        context.drawImage(video, 0, 0, canvas.width, canvas.height);
        
        const imgData = canvas.toDataURL('image/jpeg'); // Convertir a JPEG en Base64
        const img = document.createElement('img');
        img.src = imgData;
        displayDiv.innerHTML = '';
        displayDiv.appendChild(img);

        stopCamera();
    });

    fileInput.addEventListener('change', (event) => {
        const file = event.target.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = function (e) {
                const img = document.createElement('img');
                img.src = e.target.result;
                displayDiv.innerHTML = '';
                displayDiv.appendChild(img);
                stopCamera();
            };
            reader.readAsDataURL(file);
        }
    });

    translateButton.addEventListener('click', async () => {
        const imgElement = document.querySelector('#Id_fileDisplay img');
        if (imgElement) {
            outputField.value = "Procesando..."; // Mostrar mensaje temporal
            await sendToServer(imgElement.src);
        } else {
            alert('No hay imagen para procesar.');
        }
    });

    async function sendToServer(imageData) {
        try {
            const blob = await fetch(imageData).then(res => res.blob());
            const formData = new FormData();
            formData.append('image', blob, 'captured.jpg'); // Mantener el formato JPEG
            
            console.log("📤 Enviando imagen al servidor...");
            const response = await fetch('http://127.0.0.1:5000/upload', {
                method: 'POST',
                body: formData
            });

            if (!response.ok) throw new Error(`⚠️ Error en el servidor: ${response.status}`);

            const data = await response.json();
            console.log(`✅ Respuesta del servidor: ${data.text}`);

            // Mostrar el texto detectado en el textarea "atraducir"
            outputField.value = data.text || 'No se detectó texto.';

            if (video.srcObject) {
                startCamera(); // Solo reinicia la cámara si se usó antes
            }
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
});
