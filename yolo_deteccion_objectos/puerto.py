from flask import Flask, Response, render_template_string
import cv2
import torch
from ultralytics import YOLO

app = Flask(__name__)

# Configurar el dispositivo
device = "cuda" if torch.cuda.is_available() else "cpu"
model = YOLO("yolov8s.pt")
model.to(device).half() if device == "cuda" else model.to(device)

# Traducción de clases al español
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

# Configurar la cámara
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

def gen_frames():
    while True:
        success, frame = cap.read()
        if not success:
            break

        results = model(frame, imgsz=640, conf=0.75, iou=0.3, device=device)

        for result in results:
            for box in result.boxes:
                class_id = int(box.cls[0])
                label = model.names[class_id]
                label_esp = clases_esp.get(label, label)

                x1, y1, x2, y2 = map(int, box.xyxy[0])
                conf = float(box.conf[0])
                text = f"{label_esp} {conf:.2f}"

                color = (0, 255, 0) if label == "person" else (255, 0, 0)
                cv2.rectangle(frame, (x1, y1), (x2, y2), color, 3)

                (text_width, text_height), _ = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2)
                cv2.rectangle(frame, (x1, y1 - text_height - 10), (x1 + text_width + 6, y1), color, -1)
                cv2.putText(frame, text, (x1 + 3, y1 - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2)

        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


# Ruta principal con un HTML básico
@app.route('/')
def index():
    return render_template_string("""
        <html>
        <head><title>Detección YOLOv8</title></head>
        <body style="text-align:center;">
            <h1>Detección en Tiempo Real con YOLOv8</h1>
            <img src="{{ url_for('video_feed') }}">
        </body>
        </html>
    """)

# Ruta de video
@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

# Iniciar servidor
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
