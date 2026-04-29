import cv2
import mediapipe as mp
from pose import get_pose
from angles import get_knee_angle, get_hip_angle, get_shoulder_angle

from movement import detect_exercise
from rep_counter import RepCounter
from scoring import calculate_score
from logger import log_data
from datetime import datetime

# Optional voice
# from voice import speak

from mediapipe.tasks.python import vision
try:
    mp_draw = vision.drawing_utils
    pose_connections = vision.PoseLandmarksConnections.POSE_LANDMARKS
except:
    pose_connections = []

cap = cv2.VideoCapture(0)

# Fullscreen
cv2.namedWindow("Exercise Monitor", cv2.WND_PROP_FULLSCREEN)
cv2.setWindowProperty("Exercise Monitor", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

# Initialize
counter = RepCounter()
last_logged_reps = 0

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.resize(frame, (1280, 720))
    results = get_pose(frame)

    if results.pose_landmarks and len(results.pose_landmarks) > 0:
        landmarks = results.pose_landmarks[0]

        # -------- ANGLES --------
        knee_angle = get_knee_angle(landmarks)
        hip_angle = get_hip_angle(landmarks)
        shoulder_angle = get_shoulder_angle(landmarks)

        # -------- EXERCISE --------
        exercise = detect_exercise(knee_angle, hip_angle)

        # -------- REP COUNT --------
        reps, stage = counter.update(knee_angle)

        # -------- SCORING --------
        score = calculate_score(knee_angle, hip_angle, shoulder_angle)

        # -------- LOGGING (only when rep increases) --------
        if reps > last_logged_reps:
            data = {
                "time": str(datetime.now()),
                "exercise": exercise,
                "reps": reps,
                "score": score,
                "stage": stage
            }
            log_data(data)
            last_logged_reps = reps

            # Optional voice
            # if score > 85:
            #     speak("Good form")
            # else:
            #     speak("Fix posture")

        # -------- DISPLAY --------
        cv2.putText(frame, f'Exercise: {exercise}',
                    (50, 60), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2)

        cv2.putText(frame, f'Reps: {reps}',
                    (50, 110), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0,255,0), 3)

        cv2.putText(frame, f'Knee: {int(knee_angle)}',
                    (50, 170), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255,255,0), 2)

        cv2.putText(frame, f'Hip: {int(hip_angle)}',
                    (50, 210), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255,255,0), 2)

        cv2.putText(frame, f'Shoulder: {int(shoulder_angle)}',
                    (50, 250), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255,255,0), 2)

        cv2.putText(frame, f'Score: {score}%',
                    (50, 300), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,255), 2)

        cv2.putText(frame, f'Stage: {stage}',
                    (50, 350), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,200,255), 2)

        # Draw skeleton
        h, w, _ = frame.shape
        for lm in landmarks:
            cv2.circle(frame, (int(lm.x * w), int(lm.y * h)), 4, (0, 255, 0), -1)
        for connection in pose_connections:
            # handle if connection is tuple or object
            start_idx = connection[0] if isinstance(connection, tuple) else getattr(connection, 'start', 0)
            end_idx = connection[1] if isinstance(connection, tuple) else getattr(connection, 'end', 0)
            if start_idx < len(landmarks) and end_idx < len(landmarks):
                start_pt = (int(landmarks[start_idx].x * w), int(landmarks[start_idx].y * h))
                end_pt = (int(landmarks[end_idx].x * w), int(landmarks[end_idx].y * h))
                cv2.line(frame, start_pt, end_pt, (255, 255, 255), 2)

    cv2.imshow("Exercise Monitor", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()