import cv2
import torch
from ultralytics import YOLO
from flask import Flask, Response

# ==== Configuración del modelo ====
device = "cuda" if torch.cuda.is_available() else "cpu"
model_path = "/var/www/html/yolo_objetos/yolov8s.pt"

try:
    model = YOLO(model_path)
    model.to(device)
    if device == "cuda":
        model = model.half()
    else:
        model = model.float()
except Exception as e:
    print(f"Error al cargar el modelo: {e}")
    exit(1)

# ==== Diccionario de clases en español ====
clases_esp = {
    "bicycle": "Bicicleta", "car": "Coche", "motorcycle": "Moto", "airplane": "Avión",
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
    "pizza": "Pizza", "donut": "Dona", "cake": "Pastel", "couch": "Sofá",
    "potted plant": "Planta", "bed": "Cama", "dining table": "Mesa", "toilet": "Inodoro",
    "remote": "Control Remoto", "keyboard": "Teclado", "microwave": "Microondas",
    "oven": "Horno", "toaster": "Tostadora", "sink": "Fregadero",
    "vase": "Jarrón", "scissors": "Tijeras", "teddy bear": "Oso de Peluche",
    "hair drier": "Secador de Pelo", "toothbrush": "Cepillo de Dientes"
}

# ==== Inicializar la cámara ====
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 800)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 800)
cap.set(cv2.CAP_PROP_FPS, 30)

# ==== Flask App ====
app = Flask(__name__)

frame_count = 0

def gen_frames():
    global frame_count
    while True:
        success, frame = cap.read()
        if not success:
            break

        frame_count += 1
        if frame_count % 2 == 0:  # Detectar cada 3 frames
            results = model(frame, imgsz=320, conf=0.5, iou=0.4, device=device)

            for result in results:
                for box in result.boxes:
                    class_id = int(box.cls[0])
                    label = model.names[class_id]

                    if label == "person":
                        continue

                    label_esp = clases_esp.get(label, label)
                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                    conf = float(box.conf[0])

                    if conf > 0.6:  # Mostrar solo si la confianza es alta
                        texto = f"{label_esp} {conf:.2f}"
                        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                        cv2.putText(frame, texto, (x1, y1 - 10),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

        _, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/')
def index():
    return Response(gen_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

# ==== Ejecutar la app ====
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
