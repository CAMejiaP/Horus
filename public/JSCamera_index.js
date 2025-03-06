document.addEventListener('DOMContentLoaded', async () => {
    const video = document.getElementById('camera');
    const captureButton = document.getElementById('capture');
    const processButton = document.getElementById('processImage');
    const previewImage = document.getElementById('preview');
    const output = document.getElementById('output');

    async function startCamera() {
        try {
            const constraints = {
                video: {
                    width: { ideal: 1280 },
                    height: { ideal: 720 },
                    facingMode: "environment"
                }
            };

            const stream = await navigator.mediaDevices.getUserMedia(constraints);
            video.srcObject = stream;
            await video.play();
        } catch (error) {
            console.error("Error al acceder a la cámara:", error);
            alert("No se pudo acceder a la cámara. Verifica los permisos.");
        }
    }

    let capturedImageURL = "";

    captureButton.addEventListener('click', async () => {
        previewImage.src = "";
        previewImage.style.display = 'none';

        const canvas = document.createElement("canvas");
        const context = canvas.getContext("2d");

        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
        context.drawImage(video, 0, 0, canvas.width, canvas.height);

        capturedImageURL = canvas.toDataURL("image/png"); // Guardamos la imagen en una variable
        previewImage.src = capturedImageURL;
        previewImage.style.display = 'block';
    });

    processButton.addEventListener('click', async () => {
        if (!capturedImageURL) {
            alert("Primero toma una foto.");
            return;
        }

        // Convertir la imagen a un formato Blob para enviarla al servidor
        const blob = await fetch(capturedImageURL).then(res => res.blob());
        const formData = new FormData();
        formData.append("image", blob, "captured.png");

        try {
            const response = await fetch("http://127.0.0.1:5000/upload", {
                method: "POST",
                body: formData
            });

            if (!response.ok) throw new Error("Error en la respuesta del servidor");

            const data = await response.json();
            output.innerText = "Texto detectado: " + (data.text || "No se detectó texto.");
        } catch (error) {
            console.error("Error procesando la imagen:", error);
            output.innerText = "Error procesando la imagen.";
        }
    });

    startCamera();
});
