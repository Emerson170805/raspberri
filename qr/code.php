<?php
if ($_SERVER['REQUEST_METHOD'] == 'POST' && isset($_POST['texto'])) {
    // Capturar el texto ingresado para generar el QR
    $texto = urlencode($_POST['texto']);
    $qrURL = "https://api.qrserver.com/v1/create-qr-code/?size=300x300&data=$texto";
    $descargar = "codigo_qr.png"; // Nombre del archivo para descargar
}
?>
    
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Generador de Código QR</title>
    <!-- Incluir Bootstrap 5 -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body {
            font-family: Arial, sans-serif;
        }
        .container {
            margin-top: 50px;
        }
        .qr-image {
            margin-top: 20px;
        }
        .download-link {
            margin-top: 20px;
        }
    </style>
</head>
<body>

<div class="container text-center">
    <h1 class="mb-4">Generador de Código QR</h1>

    <!-- Formulario para ingresar texto y generar el código QR -->
    <form method="POST" action="" id="formularioQR" class="mb-4">
        <div class="mb-3">
            <input type="text" name="texto" id="inputTexto" class="form-control" placeholder="Introduce el texto o número" required>
        </div>
        <button type="submit" class="btn btn-primary">Generar Código QR</button>
    </form>

    <?php if (isset($qrURL)): ?>
        <!-- Mostrar el código QR generado -->
        <div class="qr-image">
            <img src="<?php echo $qrURL; ?>" alt="Código QR generado" class="img-fluid">
        </div>

        <!-- Enlace para descargar el código QR -->
        <div class="download-link">
            <a href="<?php echo $qrURL; ?>" download="<?php echo $descargar; ?>" class="btn btn-success">Descargar Código QR (PNG)</a>
        </div>
    <?php endif; ?>
</div>

<!-- Incluir Bootstrap JS y dependencias -->
<script src="https://cdn.jsdelivr.net/npm/@popperjs/core@2.11.6/dist/umd/popper.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/js/bootstrap.min.js"></script>

</body>
</html>
