import cv2
import mediapipe as mp
import numpy as np
import tensorflow as tf
import pickle
import os

# ---------- PATHS ----------
BASE_DIR = os.path.dirname(__file__)
MODEL_PATH = os.path.join(BASE_DIR, "..", "model", "gesture_model.h5")
ENCODER_PATH = os.path.join(BASE_DIR, "..", "model", "label_encoder.pkl")

model = tf.keras.models.load_model(MODEL_PATH)
with open(ENCODER_PATH, "rb") as f:
    encoder = pickle.load(f)

# ---------- MEDIAPIPE ----------
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1)
draw = mp.solutions.drawing_utils

# ---------- CAMERA ----------
cap = cv2.VideoCapture(0)

# ---------- SENTENCE LOGIC ----------
sentence = []
last_prediction = ""
stable_count = 0
STABLE_THRESHOLD = 15

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = hands.process(rgb)

    gesture_text = ""

    if result.multi_hand_landmarks:
        for hand_landmarks in result.multi_hand_landmarks:
            draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            landmarks = []
            for lm in hand_landmarks.landmark:
                landmarks.extend([lm.x, lm.y, lm.z])

            X_input = np.array(landmarks).reshape(1, -1)
            prediction = model.predict(X_input, verbose=0)
            class_id = np.argmax(prediction)
            gesture_text = encoder.inverse_transform([class_id])[0]

            # ---- STABILITY CHECK ----
            if gesture_text == last_prediction:
                stable_count += 1
            else:
                stable_count = 0
                last_prediction = gesture_text

            if stable_count == STABLE_THRESHOLD:
                if len(sentence) == 0 or sentence[-1] != gesture_text:
                    sentence.append(gesture_text)

    # ---------- DRAW SUBTITLE BAR ----------
    h, w, _ = frame.shape
    cv2.rectangle(frame, (0, h - 60), (w, h), (255,255,255), -1)

    subtitle = " ".join(sentence[-6:])
    cv2.putText(
        frame,
        subtitle,
        (10, h - 20),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.9,
        (0, 0, 0),
        2
    )

    cv2.imshow("Sign Language Subtitles", frame)

    key = cv2.waitKey(1) & 0xFF
    if key == ord("q"):
        break
    elif key == ord("c"):
        sentence.clear()  # clear sentence

cap.release()
cv2.destroyAllWindows()
