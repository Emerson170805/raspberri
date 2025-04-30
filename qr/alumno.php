<?php
// Conexión a la base de datos (ajusta según tu configuración)
$conexion = new mysqli("localhost", "emerson", "77127859", "ALUMNO_QR");
if ($conexion->connect_error) {
    die("Error de conexión: " . $conexion->connect_error);
}

$mensaje = "";
$qrURL = "";

if ($_SERVER['REQUEST_METHOD'] == 'POST') {
    $nombre = $_POST['nombre'];
    $apellido = $_POST['apellido'];
    $id_grado = $_POST['id_grado'];
    $id_seccion = $_POST['id_seccion'];
    $edad = $_POST['edad'];
    $fecha = $_POST['fecha'];
    $hora = $_POST['hora'];
    $n_whatsapp = $_POST['n_whatsapp'];
    $clave = $_POST['clave'];

    $stmt = $conexion->prepare("INSERT INTO alumnos (nombre, apellido, id_grado, id_seccion, edad, fecha, hora, n_whatsapp, clave) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)");
    $stmt->bind_param("ssiiissss", $nombre, $apellido, $id_grado, $id_seccion, $edad, $fecha, $hora, $n_whatsapp, $clave);

    if ($stmt->execute()) {
        $mensaje = "✅ Alumno registrado correctamente.";
        $qrURL = "https://api.qrserver.com/v1/create-qr-code/?size=300x300&data=" . urlencode($clave);
    } else {
        $mensaje = "❌ Error al registrar: " . $stmt->error;
    }
    $stmt->close();
}
?>

<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>Registrar Alumno</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body {
            background-color: #f7f7f7;
            font-family: Arial;
        }
        .container {
            margin-top: 40px;
        }
        .qr-image {
            margin-top: 20px;
        }
    </style>
</head>
<body>
<div class="container">
    <h2 class="text-center mb-4">Registrar Nuevo Alumno</h2>

    <?php if ($mensaje): ?>
        <div class="alert alert-info"><?php echo $mensaje; ?></div>
    <?php endif; ?>

    <form method="POST" class="row g-3">
        <div class="col-md-6">
            <input type="text" name="nombre" class="form-control" placeholder="Nombre" required>
        </div>
        <div class="col-md-6">
            <input type="text" name="apellido" class="form-control" placeholder="Apellido" required>
        </div>
        <div class="col-md-6">
            <input type="number" name="id_grado" class="form-control" placeholder="ID Grado" required>
        </div>
        <div class="col-md-6">
            <input type="number" name="id_seccion" class="form-control" placeholder="ID Sección" required>
        </div>
        <div class="col-md-4">
            <input type="number" name="edad" class="form-control" placeholder="Edad" required>
        </div>
        <div class="col-md-4">
            <input type="date" name="fecha" class="form-control" required>
        </div>
        <div class="col-md-4">
            <input type="time" name="hora" class="form-control" required>
        </div>
        <div class="col-md-6">
            <input type="text" name="n_whatsapp" class="form-control" placeholder="N° WhatsApp" required>
        </div>
        <div class="col-md-6">
            <input type="text" name="clave" class="form-control" placeholder="Clave" required>
        </div>
        <div class="col-12 text-center">
            <button type="submit" class="btn btn-primary">Registrar Alumno</button>
        </div>
    </form>

    <?php if ($qrURL): ?>
        <div class="text-center qr-image">
            <h5 class="mt-4">Código QR de la Clave</h5>
            <img src="<?php echo $qrURL; ?>" alt="QR generado">
            <div class="mt-2">
                <a href="<?php echo $qrURL; ?>" download="clave_qr.png" class="btn btn-success">Descargar QR</a>
            </div>
        </div>
    <?php endif; ?>
</div>
</body>
</html>
