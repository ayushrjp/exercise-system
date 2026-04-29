def detect_exercise(knee_angle, hip_angle):
    if knee_angle < 100 and hip_angle < 120:
        return "squat"
    else:
        return "idle"