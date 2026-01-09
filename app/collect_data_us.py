import cv2
import mediapipe as mp
import csv
import os

# ========= CONFIG =========
GESTURE_NAME = "B"   # CHANGE THIS EACH TIME
SAMPLES = 200            # Number of samples per gesture
DATA_DIR = "../data/raw1"
# ==========================

os.makedirs(DATA_DIR, exist_ok=True)
csv_path = os.path.join(DATA_DIR, f"{GESTURE_NAME}.csv")

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=1,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7
)

cap = cv2.VideoCapture(0)
count = 0

with open(csv_path, mode="w", newline="") as f:
    writer = csv.writer(f)

    while cap.isOpened() and count < SAMPLES:
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.flip(frame, 1)
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result = hands.process(rgb)

        if result.multi_hand_landmarks:
            for hand_landmarks in result.multi_hand_landmarks:
                row = []
                for lm in hand_landmarks.landmark:
                    row.extend([lm.x, lm.y, lm.z])

                row.append(GESTURE_NAME)
                writer.writerow(row)

                count += 1
                cv2.putText(
                    frame,
                    f"Collecting {GESTURE_NAME}: {count}/{SAMPLES}",
                    (10, 40),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1,
                    (0, 0, 0),
                    2
                )

        cv2.imshow("Data Collection", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

cap.release()
cv2.destroyAllWindows()
