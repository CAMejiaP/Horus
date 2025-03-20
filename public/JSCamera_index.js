document.addEventListener('DOMContentLoaded', async () => {
    const video = document.getElementById('cameraView');
    const captureButton = document.getElementById('camera');
    const fileInput = document.getElementById('fileInput');
    const translateButton = document.getElementById('atraducir');
    const outputField = document.querySelector('#atraducir');
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
            console.error('Error al acceder a la cámara:', error);
            alert('No se pudo acceder a la cámara. Verifica los permisos.');
        }
    }

    captureButton.addEventListener('click', async () => {
        if (!video.srcObject) {
            await startCamera();
        }
        
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
        context.drawImage(video, 0, 0, canvas.width, canvas.height);
        
        const imgData = canvas.toDataURL('image/png');
        const img = document.createElement('img');
        img.src = imgData;
        displayDiv.innerHTML = '';
        displayDiv.appendChild(img);

        // Detener la cámara
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
            await sendToServer(imgElement.src);
        } else {
            alert('No hay imagen para procesar.');
        }
    });

    async function sendToServer(imageData) {
        try {
            const blob = await fetch(imageData).then(res => res.blob());
            const formData = new FormData();
            formData.append('image', blob, 'captured.png');
            
            const response = await fetch('http://127.0.0.1:5000/upload', {
                method: 'POST',
                body: formData
            });

            if (!response.ok) throw new Error('Error en la respuesta del servidor');

            const data = await response.json();
            outputField.value = data.text || 'No se detectó texto.';
            
            // Reiniciar la cámara después de procesar la imagen
            startCamera();
        } catch (error) {
            console.error('Error procesando la imagen:', error);
            outputField.value = 'Error procesando la imagen.';
            startCamera();
        }
    }

    function stopCamera() {
        const stream = video.srcObject;
        if (stream) {
            const tracks = stream.getTracks();
            tracks.forEach(track => track.stop());
            video.srcObject = null;
        }
    }

    startCamera();
});
