import numpy as np

def calculate_angle(a, b, c):
    a = np.array(a)
    b = np.array(b)
    c = np.array(c)

    radians = np.arctan2(c[1]-b[1], c[0]-b[0]) - \
              np.arctan2(a[1]-b[1], a[0]-b[0])

    angle = np.abs(radians * 180.0 / np.pi)

    if angle > 180:
        angle = 360 - angle

    return angle


# Landmark indices
RIGHT_SHOULDER = 12
RIGHT_ELBOW = 14
RIGHT_HIP = 24
RIGHT_KNEE = 26
RIGHT_ANKLE = 28

def get_knee_angle(landmarks):
    hip = [landmarks[RIGHT_HIP].x, landmarks[RIGHT_HIP].y]
    knee = [landmarks[RIGHT_KNEE].x, landmarks[RIGHT_KNEE].y]
    ankle = [landmarks[RIGHT_ANKLE].x, landmarks[RIGHT_ANKLE].y]
    return calculate_angle(hip, knee, ankle)

def get_hip_angle(landmarks):
    shoulder = [landmarks[RIGHT_SHOULDER].x, landmarks[RIGHT_SHOULDER].y]
    hip = [landmarks[RIGHT_HIP].x, landmarks[RIGHT_HIP].y]
    knee = [landmarks[RIGHT_KNEE].x, landmarks[RIGHT_KNEE].y]
    return calculate_angle(shoulder, hip, knee)

def get_shoulder_angle(landmarks):
    hip = [landmarks[RIGHT_HIP].x, landmarks[RIGHT_HIP].y]
    shoulder = [landmarks[RIGHT_SHOULDER].x, landmarks[RIGHT_SHOULDER].y]
    elbow = [landmarks[RIGHT_ELBOW].x, landmarks[RIGHT_ELBOW].y]
    return calculate_angle(hip, shoulder, elbow)