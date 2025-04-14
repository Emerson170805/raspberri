import cv2
import numpy as np
import tensorflow as tf
import mediapipe as mp

def main():
    # CARGANDO EL MODELO DEL ENTRENAMIENTO
    modelo = tf.keras.models.load_model('modelo_emociones.h5')
    etiquetas = ['feliz', 'neutral', 'sorprendido', 'triste']

    # VA A UTILIZAR LA CAMARA 2
    cap = cv2.VideoCapture(2)
    if not cap.isOpened():
        print("❌ No se pudo abrir la cámara.")
        return

    # INICIA LA LIBRERIA MEDIAPIPE
    mp_face_mesh = mp.solutions.face_mesh
    face_mesh = mp_face_mesh.FaceMesh(static_image_mode=False, max_num_faces=5, min_detection_confidence=0.5)

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                print("❌ Error al capturar imagen.")
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

                    # USA MALLA FACIAL
                    for punto in puntos:
                        cv2.circle(frame, punto, 1, (0, 255, 0), -1)

                    # VA A MOSTRAR LA EMOCION EN ARRIBA DEL RECUADRO
                    cv2.putText(frame, emocion, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 255), 2)

            # ASEGURAR QUE SE HABRA UNA VENTANA NOMA
            cv2.imshow("Detector de emociones", frame)
            if cv2.waitKey(1) & 0xFF == 27:  # ESC para salir
                break
    finally:
        cap.release()
        cv2.destroyAllWindows()
        face_mesh.close()

if __name__ == "__main__":
    main()
