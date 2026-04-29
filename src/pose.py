import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import os

model_path = os.path.join(os.path.dirname(__file__), 'pose_landmarker.task')

if not os.path.exists(model_path):
    print(f"CRITICAL ERROR: MediaPipe model file not found at {model_path}")
    landmarker = None
else:
    try:
        base_options = python.BaseOptions(model_asset_path=model_path)
        options = vision.PoseLandmarkerOptions(
            base_options=base_options,
            running_mode=vision.RunningMode.IMAGE)
        landmarker = vision.PoseLandmarker.create_from_options(options)
        print("MediaPipe Pose Landmarker initialized successfully.")
    except Exception as e:
        print(f"CRITICAL ERROR: Failed to initialize MediaPipe - {e}")
        landmarker = None

def get_pose(frame):
    if landmarker is None:
        class DummyResults: 
            pose_landmarks = []
        return DummyResults()
    try:
        # Tasks API requires RGB Image
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
        return landmarker.detect(mp_image)
    except Exception as e:
        print(f"Error during pose detection: {e}")
        class DummyResults: 
            pose_landmarks = []
        return DummyResults()