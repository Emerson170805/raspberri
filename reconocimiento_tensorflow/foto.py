from flask import Flask, Response
import cv2
import numpy as np
import tensorflow as tf
import mediapipe as mp

app = Flask(__name__)

# Cargar modelo
modelo = tf.keras.models.load_model('modelo_emociones.h5')
etiquetas = ['feliz', 'neutral', 'sorprendido', 'triste']

# Iniciar cámara (usa 2 si tienes varias cámaras, cambia si es necesario)
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    raise RuntimeError("❌ No se pudo abrir la cámara.")

# Iniciar MediaPipe Face Mesh
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(static_image_mode=False, max_num_faces=5, min_detection_confidence=0.5)

def procesar_emociones():
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        resultados = face_mesh.process(rgb)

        if resultados.multi_face_landmarks:
            h, w, _ = frame.shape
            for rostro in resultados.multi_face_landmarks:
                puntos = [(int(p.x * w), int(p.y * h)) for p in rostro.landmark]
                xs, ys = zip(*puntos)
                x1, y1 = max(min(xs) - 10, 0), max(min(ys) - 10, 0)
                x2, y2 = min(max(xs) + 10, w), min(max(ys) + 10, h)

                rostro_img = frame[y1:y2, x1:x2]
                if rostro_img.size == 0:
                    continue

                gris = cv2.cvtColor(rostro_img, cv2.COLOR_BGR2GRAY)
                redimensionado = cv2.resize(gris, (48, 48)) / 255.0
                entrada = np.expand_dims(np.expand_dims(redimensionado, -1), 0)

                pred = modelo.predict(entrada, verbose=0)
                emocion = etiquetas[np.argmax(pred)]

                for punto in puntos:
                    cv2.circle(frame, punto, 1, (0, 255, 0), -1)

                cv2.putText(frame, emocion, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 255), 2)

        # Convertir frame a JPEG
        _, buffer = cv2.imencode('.jpg', frame)
        frame_bytes = buffer.tobytes()

        # Enviar como stream
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

@app.route('/')
def index():
    return "<h1>Detector de Emociones</h1><img src='/video'>"

@app.route('/video')
def video():
    return Response(procesar_emociones(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
