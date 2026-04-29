def calculate_score(knee_angle, hip_angle, shoulder_angle):
    knee_score = 100 if 70 <= knee_angle <= 100 else max(0, 100 - abs(knee_angle - 85))
    hip_score = 100 if 70 <= hip_angle <= 110 else max(0, 100 - abs(hip_angle - 90))
    shoulder_score = 100 if 20 <= shoulder_angle <= 60 else max(0, 100 - abs(shoulder_angle - 40))

    final_score = int(0.5 * knee_score + 0.3 * hip_score + 0.2 * shoulder_score)
    return final_score