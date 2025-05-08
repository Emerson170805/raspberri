import cv2
import mediapipe as mp
import joblib
import numpy as np
import sys
from flask import Flask, jsonify
from RPLCD.gpio import CharLCD
from RPi import GPIO
from time import sleep
from multiprocessing import Process, Manager

# ================= FUNCIONES DE VISIÓN =================
def normalize_landmarks(landmarks):
    landmarks = np.array(landmarks).reshape(-1, 3)
    wrist = landmarks[0]
    landmarks -= wrist
    max_value = np.max(np.abs(landmarks))
    if max_value != 0:
        landmarks /= max_value
    return landmarks.flatten().tolist()

# =================== FLASK ===================
def start_flask_server(shared_label):
    app = Flask(__name__)

    @app.route('/gesto', methods=['GET'])
    def get_gesto():
        return jsonify({'gesto': shared_label.value})

    print("🌐 Servidor iniciado en http://<IP_Raspberry>:5000/gesto")
    app.run(host='0.0.0.0', port=5000)

# =============== DETECCIÓN DE GESTOS ================
def gesture_recognition(shared_label):
    try:
        model = joblib.load('model/gesture_svm.pkl')
        le = joblib.load('model/label_encoder.pkl')
        print("✅ Modelo y encoder cargados correctamente")
    except Exception as e:
        print(f"❌ Error al cargar modelos: {e}")
        sys.exit(1)

    mp_hands = mp.solutions.hands
    hands = mp_hands.Hands(False, 1, 0.7, 0.5)
    mp_draw = mp.solutions.drawing_utils

    # LCD Config
    lcd = CharLCD(cols=16, rows=2, pin_rs=26, pin_e=19,
                  pins_data=[13, 6, 5, 11], numbering_mode=GPIO.BCM)
    lcd.clear()
    lcd.write_string("Iniciando...")

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("❌ No se pudo abrir la cámara")
        return

    current_display = ""
    
    while True:
        ret, frame = cap.read()
        if not ret:
            continue

        frame = cv2.flip(frame, 1)
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result = hands.process(rgb)

        if result.multi_hand_landmarks:
            for handLms in result.multi_hand_landmarks:
                mp_draw.draw_landmarks(frame, handLms, mp_hands.HAND_CONNECTIONS)

                landmarks = [coord for lm in handLms.landmark for coord in (lm.x, lm.y, lm.z)]
                if len(landmarks) == 63:
                    try:
                        norm_landmarks = normalize_landmarks(landmarks)
                        pred = model.predict([norm_landmarks])[0]
                        label = le.inverse_transform([pred])[0]
                        shared_label.value = label

                        # Actualizar LCD solo si cambia el gesto
                        if label != current_display:
                            current_display = label
                            lcd.clear()
                            lcd.write_string(f'Gesto:\n{label}')
                    except Exception as e:
                        print(f"⚠️ Error predicción: {e}")
        else:
            shared_label.value = "Sin mano"

        cv2.putText(frame, f'Gesto: {shared_label.value}', (10, 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        cv2.imshow("Gestos", frame)

        if cv2.waitKey(10) == 27:  # ESC
            break

    cap.release()
    cv2.destroyAllWindows()
    lcd.clear()

# ================== MAIN ==================
if __name__ == '__main__':
    with Manager() as manager:
        shared_label = manager.Value('u', 'Cargando...')

        flask_process = Process(target=start_flask_server, args=(shared_label,))
        vision_process = Process(target=gesture_recognition, args=(shared_label,))

        flask_process.start()
        vision_process.start()

        vision_process.join()
        flask_process.terminate()
