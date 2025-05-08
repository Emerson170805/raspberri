from flask import Flask, render_template, Response, jsonify
import cv2
import mediapipe as mp
import joblib
import numpy as np
from RPLCD.gpio import CharLCD
from RPi import GPIO
from time import sleep, time

# ------------------ CONFIGURACIÓN LCD ------------------
lcd = CharLCD(
    cols=16, rows=2,
    pin_rs=26,
    pin_e=19,
    pins_data=[13, 6, 5, 11],
    numbering_mode=GPIO.BCM
)
lcd.clear()
lcd.write_string('Iniciando...')
sleep(2)
lcd.clear()

# ------------------ VARIABLES GLOBALES ------------------
gesto_actual = ""
texto_completo = ""  # Inicializado correctamente
ultimo_gesto = ""
tiempo_inicio = time()

# ------------------ CARGA DE MODELOS ------------------
try:
    model = joblib.load('model/gesture_svm.pkl')
    le = joblib.load('model/label_encoder.pkl')
    print("✅ Modelo y encoder cargados correctamente")
except Exception as e:
    print(f"❌ Error al cargar los modelos: {e}")
    exit(1)

# ------------------ CONFIGURAR FLASK Y MEDIAPIPE ------------------
app = Flask(__name__)
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=1,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.5
)
mp_draw = mp.solutions.drawing_utils
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 500)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 500)

# ------------------ FUNCIONES ------------------
def normalize_landmarks(landmarks):
    landmarks = np.array(landmarks).reshape(-1, 3)
    wrist = landmarks[0]
    landmarks -= wrist
    max_value = np.max(np.abs(landmarks))
    if max_value != 0:
        landmarks /= max_value
    return landmarks.flatten().tolist()

def centrar(texto):
    if len(texto) >= 16:
        return texto[:16]
    espacio = (16 - len(texto)) // 2
    return ' ' * espacio + texto

def actualizar_lcd(gesto):
    lcd.clear()
    lcd.cursor_pos = (0, 0)
    lcd.write_string(centrar(gesto))
    lcd.cursor_pos = (1, 0)
    lcd.write_string(centrar("Gesto detectado"))

def generate_frames():
    global gesto_actual, texto_completo, ultimo_gesto, tiempo_inicio

    while True:
        success, frame = cap.read()
        if not success:
            break

        frame = cv2.flip(frame, 1)
        img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result = hands.process(img_rgb)

        if result.multi_hand_landmarks:
            for handLms in result.multi_hand_landmarks:
                mp_draw.draw_landmarks(frame, handLms, mp_hands.HAND_CONNECTIONS)
                landmarks = [coord for lm in handLms.landmark for coord in (lm.x, lm.y, lm.z)]

                if len(landmarks) == 63:
                    try:
                        norm_landmarks = normalize_landmarks(landmarks)
                        pred = model.predict([norm_landmarks])[0]
                        label = le.inverse_transform([pred])[0]
                        gesto_actual = label

                        if label == ultimo_gesto:
                            if time() - tiempo_inicio >= 2:
                                if label.lower() == "espacio":
                                    texto_completo += " "
                                elif label.lower() == "borrar":
                                    if texto_completo:
                                        texto_completo = texto_completo[:-1]
                                else:
                                    texto_completo += label
                                actualizar_lcd(label)
                                tiempo_inicio = time() + 9999  # Para evitar repetición inmediata
                        else:
                            ultimo_gesto = label
                            tiempo_inicio = time()
                        

                        cv2.putText(frame, f'Gesto: {label}', (10, 50),
                                    cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)

                    except Exception as e:
                        print(f"⚠️ Error en predicción: {e}")

        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

# ------------------ RUTAS FLASK ------------------
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/apagarlcd')
def apagar_lcd():
    lcd.clear()
    lcd.write_string(centrar("Listo :)"))
    sleep(2)
    lcd.clear()
    return "LCD limpiado"

@app.route('/texto_actual')
def texto_actual_route():
    global texto_completo
    return jsonify({"texto": texto_completo})

@app.route('/borrar_texto')
def borrar_texto():
    global texto_completo
    texto_completo = ""
    return "Texto borrado"

@app.route('/gesto_actual')
def obtener_gesto():
    return jsonify({"gesto": gesto_actual})

# ------------------ INICIAR APP ------------------
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
