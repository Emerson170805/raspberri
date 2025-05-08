from flask import Flask, Response, render_template_string
import cv2
import torch
from ultralytics import YOLO

app = Flask(__name__)

# ✅ Configuración del modelo y dispositivo
# En Raspberry Pi no tenemos GPU, por lo tanto usamos solo CPU
device = "cpu"

# ✅ Cargar el modelo más ligero para Raspberry Pi
# 'yolov8n.pt' = Nano, mucho más liviano y rápido que 's' o 'm'
model = YOLO("yolov8n.pt")
model.to(device)  # Asegurar que el modelo corre en CPU

# ✅ Diccionario reducido de clases traducidas al español (solo lo necesario)
clases_esp = {
    "person": "Persona", "bicycle": "Bicicleta", "car": "Coche", "motorcycle": "Moto", "airplane": "Avión",
    "bus": "Autobús", "train": "Tren", "truck": "Camión", "boat": "Barco",
    "tv": "Televisor", "laptop": "Laptop", "mouse": "Ratón", "cell phone": "Celular",
    "refrigerator": "Refrigerador", "chair": "Silla", "book": "Libro", "clock": "Reloj",
    "parking meter": "Parquímetro", "bench": "Banco", "bird": "Pájaro", "cat": "Gato",
    "dog": "Perro", "horse": "Caballo", "sheep": "Oveja", "cow": "Vaca",
    "elephant": "Elefante", "bear": "Oso", "zebra": "Cebra", "giraffe": "Jirafa",
    "backpack": "Mochila", "umbrella": "Paraguas", "handbag": "Bolso", "tie": "Corbata",
    "suitcase": "Maleta", "frisbee": "Frisbee", "skis": "Esquís", "snowboard": "Snowboard",
    "sports ball": "Balón", "kite": "Cometa", "baseball bat": "Bate de Béisbol",
    "baseball glove": "Guante de Béisbol", "skateboard": "Patineta",
    "surfboard": "Tabla de Surf", "tennis racket": "Raqueta de Tenis",
    "bottle": "Botella", "wine glass": "Copa de Vino", "cup": "Taza",
    "fork": "Tenedor", "knife": "Cuchillo", "spoon": "Cuchara", "bowl": "Tazón",
    "banana": "Banana", "apple": "Manzana", "sandwich": "Sándwich", "orange": "Naranja",
    "broccoli": "Brócoli", "carrot": "Zanahoria", "hot dog": "Hot Dog",
    "pizza": "Pizza", "donut": "Dona", "cake": "Pastel", "chair": "Silla",
    "couch": "Sofá", "potted plant": "Planta", "bed": "Cama",
    "dining table": "Mesa", "toilet": "Inodoro", "tv": "Televisor",
    "laptop": "Laptop", "mouse": "Ratón", "remote": "Control Remoto",
    "keyboard": "Teclado", "cell phone": "Celular", "microwave": "Microondas",
    "oven": "Horno", "toaster": "Tostadora", "sink": "Fregadero",
    "refrigerator": "Refrigerador", "book": "Libro", "clock": "Reloj",
    "vase": "Jarrón", "scissors": "Tijeras", "teddy bear": "Oso de Peluche",
    "hair drier": "Secador de Pelo", "toothbrush": "Cepillo de Dientes",
}

# ✅ Configurar la cámara (webcam) a una resolución baja para ganar fluidez
# Cuanto menor sea la resolución, menor será el procesamiento necesario
cap = cv2.VideoCapture(0)  # Cambiar si usas una cámara USB diferente
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 500)   # Ancho reducido
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 250)  # Alto reducido

def gen_frames():
    while True:
        success, frame = cap.read()
        if not success:
            break

        # ✅ Ejecutar la detección con resolución de entrada menor
        # imgsz = 416 es más rápido que usar 640 o 720
        # conf = 0.5 filtra solo detecciones con más de 50% de confianza
        results = model(frame, imgsz=416, conf=0.1, iou=0.3, device=device)

        for result in results:
            for box in result.boxes:
                class_id = int(box.cls[0])
                label = model.names[class_id]
                label_esp = clases_esp.get(label, label)

                x1, y1, x2, y2 = map(int, box.xyxy[0])
                conf = float(box.conf[0])
                text = f"{label_esp} {conf:.2f}"

                if conf < 0.5:
                    continue  # ✅ Ignorar objetos con baja probabilidad

                # ✅ Colores personalizados: verde para personas, azul para otros
                color = (0, 255, 0) if label == "person" else (255, 0, 0)
                cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)

                # ✅ Mostrar texto encima del objeto detectado
                (text_width, text_height), _ = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
                cv2.rectangle(frame, (x1, y1 - text_height - 6), (x1 + text_width + 4, y1), color, -1)
                cv2.putText(frame, text, (x1 + 2, y1 - 2), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)

        # ✅ Codificar el frame para transmitirlo al navegador
        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

# ✅ Página web básica para mostrar el video
@app.route('/')
def index():
    return render_template_string("""
        <html>
        <head><title>YOLOv8 en Raspberry Pi</title></head>
        <body style="text-align:center;">
            <h2>Detección en Tiempo Real - Raspberry Pi 4</h2>
            <img src="{{ url_for('video_feed') }}" style="border:2px solid black;">
        </body>
        </html>
    """)

# ✅ Ruta de video en tiempo real
@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

# ✅ Ejecutar la app Flask en modo multihilo para no bloquear
if __name__ == '__main__':
    # 'threaded=True' mejora el rendimiento de Flask en la Pi
    app.run(host='0.0.0.0', port=5000, threaded=True)
