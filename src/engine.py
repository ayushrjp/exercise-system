import cv2
import time
from pose import get_pose
from angles import get_knee_angle, get_hip_angle, get_shoulder_angle
from movement import detect_exercise
from rep_counter import RepCounter
from scoring import calculate_score
from logger import log_data
from datetime import datetime
from mediapipe.tasks.python import vision

try:
    mp_draw = vision.drawing_utils
    pose_connections = vision.PoseLandmarksConnections.POSE_LANDMARKS
except:
    pose_connections = []

class FitnessEngine:
    def __init__(self):
        # Try multiple camera indices starting with 0
        self.cap = None
        for index in [0, 1, 2]:
            print(f"Attempting to open camera at index {index}...")
            # Use CAP_DSHOW on Windows for better compatibility
            self.cap = cv2.VideoCapture(index, cv2.CAP_DSHOW)
            if self.cap.isOpened():
                # Give the camera a moment to initialize and check if it actually returns frames
                success, _ = self.cap.read()
                if success:
                    print(f"Successfully opened camera at index {index}")
                    break
                else:
                    print(f"Camera index {index} opened but failed to read. Releasing...")
                    self.cap.release()
                    self.cap = None
            else:
                self.cap = None

        if not self.cap:
            print("CRITICAL: No camera device found after trying indices [0, 1, 2]")
        
        self.counter = RepCounter()
        self.last_logged_reps = 0
        self.fps = 0
        self.prev_time = 0
        self.person_detected = False
        self.latest_angles = {"knee": 0, "hip": 0, "shoulder": 0}
        self.stage = "up"
        self.current_exercise = "None"
        self.current_score = 0

        
    def get_frame(self):
        ret, frame = self.cap.read()
        if not ret or frame is None:
            # Return a blank frame if camera is unavailable
            import numpy as np
            blank_frame = np.zeros((720, 1280, 3), dtype=np.uint8)
            cv2.putText(blank_frame, "Camera Offline", (400, 360), cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255), 3)
            ret, jpeg = cv2.imencode('.jpg', blank_frame)
            return jpeg.tobytes()

        frame = cv2.resize(frame, (1280, 720))
        results = get_pose(frame)
        
        # Calculate FPS
        current_time = time.time()
        self.fps = int(1 / (current_time - self.prev_time)) if self.prev_time > 0 else 0
        self.prev_time = current_time

        if results.pose_landmarks and len(results.pose_landmarks) > 0:
            self.person_detected = True
            landmarks = results.pose_landmarks[0]

            # -------- ANGLES --------
            knee_angle = get_knee_angle(landmarks)
            hip_angle = get_hip_angle(landmarks)
            shoulder_angle = get_shoulder_angle(landmarks)

            # -------- EXERCISE --------
            exercise = detect_exercise(knee_angle, hip_angle)

            # -------- REP COUNT --------
            reps, stage = self.counter.update(knee_angle)

            # -------- SCORING --------
            score = calculate_score(knee_angle, hip_angle, shoulder_angle)
            
            # -------- UPDATE STATE --------
            self.latest_angles = {"knee": knee_angle, "hip": hip_angle, "shoulder": shoulder_angle}
            self.stage = stage
            self.current_exercise = exercise
            self.current_score = score


            # -------- LOGGING --------
            if reps > self.last_logged_reps:
                data = {
                    "time": str(datetime.now()),
                    "exercise": exercise,
                    "reps": reps,
                    "score": score,
                    "stage": stage
                }
                log_data(data)
                self.last_logged_reps = reps

            # -------- DISPLAY --------
            # We don't need text display on the video since the frontend UI shows it beautifully
            # But we will draw the skeleton and angle numbers
            h, w, _ = frame.shape
            
            # Draw skeleton
            for lm in landmarks:
                cv2.circle(frame, (int(lm.x * w), int(lm.y * h)), 5, (0, 255, 128), -1)
                
            for connection in pose_connections:
                start_idx = connection[0] if isinstance(connection, tuple) else getattr(connection, 'start', 0)
                end_idx = connection[1] if isinstance(connection, tuple) else getattr(connection, 'end', 0)
                if start_idx < len(landmarks) and end_idx < len(landmarks):
                    start_pt = (int(landmarks[start_idx].x * w), int(landmarks[start_idx].y * h))
                    end_pt = (int(landmarks[end_idx].x * w), int(landmarks[end_idx].y * h))
                    cv2.line(frame, start_pt, end_pt, (255, 255, 255), 2)
            
            # Optionally draw angles at joints
            # RIGHT_KNEE = 26
            if 26 < len(landmarks):
                kx, ky = int(landmarks[26].x * w), int(landmarks[26].y * h)
                cv2.putText(frame, str(int(knee_angle)), (kx + 10, ky + 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,255,255), 2)
                
            # RIGHT_HIP = 24
            if 24 < len(landmarks):
                hx, hy = int(landmarks[24].x * w), int(landmarks[24].y * h)
                cv2.putText(frame, str(int(hip_angle)), (hx + 10, hy + 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,255,255), 2)
                
            # RIGHT_SHOULDER = 12
            if 12 < len(landmarks):
                sx, sy = int(landmarks[12].x * w), int(landmarks[12].y * h)
                cv2.putText(frame, str(int(shoulder_angle)), (sx + 10, sy + 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,255,255), 2)
        else:
            self.person_detected = False

        ret, jpeg = cv2.imencode('.jpg', frame)
        return jpeg.tobytes()

    def get_status(self):
        return {
            "fps": self.fps,
            "person_detected": self.person_detected,
            "camera_connected": self.cap.isOpened(),
            "angles": self.latest_angles,
            "stage": self.stage,
            "exercise": self.current_exercise,
            "score": self.current_score
        }


    def __del__(self):
        self.cap.release()
