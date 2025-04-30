<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Escáner de Código QR</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body {
            padding: 2rem;
            background-color: #f8f9fa;
        }
        video {
            width: 100%;
            max-width: 400px;
            border: 4px solid #198754;
            position: relative;
        }
        .scanner-line {
            position: absolute;
            width: 90%;
            height: 3px;
            background-color: red;
            animation: scan 2s linear infinite;
            left: 5%;
            z-index: 10;
        }
        @keyframes scan {
            0% { top: 10px; }
            100% { top: 90%; }
        }
        #scanner-wrapper {
            position: relative;
            display: inline-block;
        }
    </style>
</head>
<body>

<div class="container text-center">
    <h1 class="mb-4">Escáner de Código QR</h1>

    <!-- Escaneo por cámara -->
    <div class="mb-5">
        <h4>📷 Escanear con la cámara</h4>
        <div id="scanner-wrapper">
            <video id="video" autoplay playsinline></video>
            <div class="scanner-line" id="scan-line" style="display: none;"></div>
        </div>
        <br>
        <button id="startCamera" class="btn btn-success mt-3">Iniciar cámara</button>
        <button id="stopCamera" class="btn btn-danger mt-3" style="display: none;">Detener cámara</button>
    </div>

    <!-- Escaneo por archivo -->
    <div class="mb-5">
        <h4>📁 O carga una imagen</h4>
        <input type="file" id="fileInput" accept="image/*" class="form-control w-50 mx-auto">
    </div>

    <!-- Resultado -->
    <div class="alert alert-primary" id="result">
        <strong>Resultado:</strong>
        <span id="qrResult">Esperando escaneo...</span>
    </div>
</div>

<!-- jsQR -->
<script src="https://cdn.jsdelivr.net/npm/jsqr/dist/jsQR.js"></script>

<script>
    const video = document.getElementById("video");
    const startCameraBtn = document.getElementById("startCamera");
    const stopCameraBtn = document.getElementById("stopCamera");
    const fileInput = document.getElementById("fileInput");
    const resultText = document.getElementById("qrResult");
    const scanLine = document.getElementById("scan-line");

    let stream = null;
    let scanInterval = null;

    // Iniciar cámara
    startCameraBtn.addEventListener("click", async () => {
        if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
            try {
                stream = await navigator.mediaDevices.getUserMedia({ video: { facingMode: "environment" } });
                video.srcObject = stream;
                startCameraBtn.style.display = "none";
                stopCameraBtn.style.display = "inline-block";
                scanLine.style.display = "block";

                scanInterval = setInterval(scanFromCamera, 300);
            } catch (err) {
                alert("Error al acceder a la cámara: " + err.message);
            }
        } else {
            alert("Tu navegador no soporta acceso a la cámara.");
        }
    });

    // Detener cámara
    stopCameraBtn.addEventListener("click", () => {
        if (stream) {
            stream.getTracks().forEach(track => track.stop());
        }
        video.srcObject = null;
        clearInterval(scanInterval);
        startCameraBtn.style.display = "inline-block";
        stopCameraBtn.style.display = "none";
        scanLine.style.display = "none";
    });

    // Escaneo desde la cámara
    function scanFromCamera() {
        const canvas = document.createElement("canvas");
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
        const ctx = canvas.getContext("2d");
        ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

        const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
        const qrCode = jsQR(imageData.data, canvas.width, canvas.height);

        if (qrCode) {
            resultText.textContent = qrCode.data;
        }
    }

    // Escaneo desde archivo
    fileInput.addEventListener("change", e => {
        const file = e.target.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = e => {
                const img = new Image();
                img.onload = () => {
                    const canvas = document.createElement("canvas");
                    canvas.width = img.width;
                    canvas.height = img.height;
                    const ctx = canvas.getContext("2d");
                    ctx.drawImage(img, 0, 0);
                    const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
                    const qrCode = jsQR(imageData.data, canvas.width, canvas.height);
                    resultText.textContent = qrCode ? qrCode.data : "No se detectó ningún código QR.";
                };
                img.src = e.target.result;
            };
            reader.readAsDataURL(file);
        }
    });
</script>

</body>
</html>
