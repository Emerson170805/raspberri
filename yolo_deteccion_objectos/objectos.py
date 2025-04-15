import cv2
import torch
from ultralytics import YOLO

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
cap.set(cv2.CAP_PROP_FPS, 30)

window_name = "Detección Mejorada"
cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    results = model(frame, imgsz=640, conf=0.75, iou=0.3, device=device, visualize=False)  # Ajuste en conf e iou

    for result in results:
        for box in result.boxes:
            class_id = int(box.cls[0])
            label = model.names[class_id]
            label_esp = clases_esp.get(label, label)

            x1, y1, x2, y2 = map(int, box.xyxy[0])
            conf = float(box.conf[0])
            text = f"{label_esp} {conf:.2f}"

            # Color según clase
            if label == "person":
                color = (0, 255, 0)  # Verde para personas
                label_esp = "Persona"
            else:
                color = (255, 0, 0)  # Azul para otros objetos
                label_esp = clases_esp.get(label, label)

            # Dibujar rectángulo más grueso
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 3)

            # Obtener tamaño del texto
            (text_width, text_height), _ = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2)

            # Dibujar fondo del texto
            cv2.rectangle(frame, (x1, y1 - text_height - 10), (x1 + text_width + 6, y1), color, -1)

            # Dibujar texto blanco encima del fondo
            cv2.putText(frame, text, (x1 + 3, y1 - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2)

    cv2.imshow(window_name, frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()

