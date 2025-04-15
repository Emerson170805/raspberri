from flask import Flask, Response
import cv2

app = Flask(__name__)

# Iniciar cámara (solo la cámara 0)
cap = cv2.VideoCapture(0)

# Establecer resolución 720p
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 650)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 400)

if not cap.isOpened():
    raise RuntimeError("❌ No se pudo abrir la cámara.")

def generar_video():
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Convertir frame a JPEG
        _, buffer = cv2.imencode('.jpg', frame)
        frame_bytes = buffer.tobytes()

        # Enviar como stream
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

@app.route('/')
def index():
    return "<h1>Cámara en Vivo</h1><img src='/video'>"

@app.route('/video')
def video():
    return Response(generar_video(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
