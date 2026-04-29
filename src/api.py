from flask import Flask, jsonify, request, Response, send_file, session, make_response
import json
import os
import io
import csv
from datetime import datetime, timedelta

from db import init_db, get_db_connection
import auth
 
app = Flask(__name__)

# ─── Session / Cookie Configuration ──────────────────────────────────────────
# Use Flask's built-in SIGNED COOKIE sessions (no flask-session / filesystem needed).
# This avoids the debug-reloader "two processes / shared filesystem" problem entirely.
app.secret_key = 'fitness-ai-secret-key-2024-prod'
app.config['SESSION_COOKIE_NAME'] = 'neuronfit_session'
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'      # Most compatible for localhost
app.config['SESSION_COOKIE_SECURE'] = False       # Required for HTTP
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_DOMAIN'] = None        # Let browser decide based on URL
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=31)
app.config['SESSION_REFRESH_EACH_REQUEST'] = True

# ─── Manual CORS — echo back the requesting origin ───────────────────────────
# This lets file://, localhost on any port, and same-origin all work with credentials.
@app.after_request
def add_cors_headers(response):
    origin = request.headers.get('Origin')
    if origin:
        response.headers['Access-Control-Allow-Origin'] = origin
        response.headers['Access-Control-Allow-Credentials'] = 'true'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, Cookie'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
    
    # Ensure the cookie is always allowed to be stored
    response.headers['Vary'] = 'Origin, Cookie'
    return response

@app.before_request
def handle_preflight():
    if request.method == 'OPTIONS':
        response = app.make_default_options_response()
        origin = request.headers.get('Origin')
        if origin:
            response.headers['Access-Control-Allow-Origin'] = origin
            response.headers['Access-Control-Allow-Credentials'] = 'true'
            response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, Cookie'
            response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
        return response


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FRONTEND_DIR = os.path.join(BASE_DIR, "Frontend")
DATA_FILE = os.path.join(BASE_DIR, "data/workout.json")

# Initialize Database
init_db()

# Initialize Engine
try:
    from engine import FitnessEngine
    engine = FitnessEngine()
    print("FitnessEngine initialized successfully.")
except Exception as e:
    print(f"Warning: Could not initialize FitnessEngine - {e}")
    engine = None

def read_data():
    if not os.path.exists(DATA_FILE):
        return []
    try:
        with open(DATA_FILE, "r") as f:
            content = f.read().strip()
            if not content:
                return []
            return json.loads(content)
    except Exception as e:
        print(f"Error reading data: {e}")
        return []

@app.before_request
def debug_session():
    # Print cookies for debugging (don't do this in production)
    if not request.path.startswith('/static') and not request.path == '/video_feed':
        print(f"DEBUG: Request to {request.path} | Cookies: {request.cookies.keys()}")

def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            print(f"DEBUG: login_required failed for {request.path} - user_id not in session")
            return jsonify({"error": "Authentication required"}), 401
        return f(*args, **kwargs)
    return decorated_function

# ─── Auth Endpoints ───────────────────────────────────────────────────────────

@app.route("/signup", methods=["POST"])
def signup():
    data = request.json
    name = data.get("name")
    email = data.get("email")
    password = data.get("password")

    if not name or not email or not password:
        return jsonify({"error": "Missing fields"}), 400

    if auth.get_user_by_email(email):
        return jsonify({"error": "Email already exists"}), 400

    if auth.create_user(name, email, password):
        return jsonify({"message": "User created successfully"})
    return jsonify({"error": "Failed to create user"}), 500

@app.route("/login", methods=["POST"])
def login():
    data = request.json
    email = data.get("email")
    password = data.get("password")

    user = auth.get_user_by_email(email)
    if user:
        print(f"User found: {user['email']}")
        if auth.check_password(password, user["password_hash"]):
            session.clear()
            session["user_id"] = user["id"]
            session["user_name"] = user["name"]
            session.permanent = True
            session.modified = True  # Force Flask to send the Set-Cookie header
            print(f"LOGIN SUCCESS: {user['email']} (ID: {user['id']})")
            
            resp = jsonify({"message": "Logged in", "user": {"id": user["id"], "name": user["name"]}})
            return resp
        else:
            print(f"Password mismatch for {user['email']}")
    else:
        print(f"User not found: {email}")
    return jsonify({"error": "Invalid credentials"}), 401

@app.route("/logout", methods=["POST"])
def logout():
    session.clear()
    return jsonify({"message": "Logged out"})

@app.route("/me", methods=["GET"])
def me():
    user_id = session.get("user_id")
    print(f"DEBUG /me: session keys={list(session.keys())}, user_id={user_id}")
    if not user_id:
        return jsonify({"error": "Not logged in"}), 401

    user = auth.get_user_by_id(user_id)
    if user:
        return jsonify({"id": user["id"], "name": user["name"], "email": user["email"]})
    return jsonify({"error": "User not found"}), 404

# ─── Data Endpoints (Protected) ───────────────────────────────────────────────

@app.route("/data", methods=["GET"])
@login_required
def get_data():
    return jsonify(read_data())

@app.route("/summary", methods=["GET"])
@login_required
def get_summary():
    data = read_data()
    status = engine.get_status() if engine else {
        "fps": 0, "person_detected": False, "camera_connected": False,
        "angles": {"knee": 0, "hip": 0, "shoulder": 0}, "stage": "N/A", "score": 0
    }

    if not data:
        return jsonify({
            "total_reps": 0,
            "avg_score": 0,
            "last_exercise": "None",
            "last_score": 0,
            "stage": status.get("stage", "N/A"),
            "fps": status["fps"],
            "person_detected": status["person_detected"],
            "camera_connected": status["camera_connected"],
            "angles": status.get("angles", {"knee": 0, "hip": 0, "shoulder": 0}),
            "live_score": status.get("score", 0),
            "model_running": engine is not None
        })

    latest = data[-1]
    scores = [d.get("score", 0) for d in data if "score" in d]
    avg_score = int(sum(scores) / len(scores)) if scores else 0
    best_score = max(scores) if scores else 0

    if len(scores) >= 10:
        first_avg = sum(scores[:5]) / 5
        last_avg = sum(scores[-5:]) / 5
        improvement = int(((last_avg - first_avg) / first_avg) * 100) if first_avg > 0 else 0
    else:
        improvement = 0

    try:
        session_start = datetime.strptime(data[0]["time"], "%Y-%m-%d %H:%M:%S.%f")
        session_end = datetime.strptime(latest["time"], "%Y-%m-%d %H:%M:%S.%f")
        duration_sec = int((session_end - session_start).total_seconds())
    except Exception:
        duration_sec = 0

    return jsonify({
        "total_reps": latest.get("reps", 0),
        "avg_score": avg_score,
        "best_score": best_score,
        "improvement_pct": improvement,
        "duration_sec": duration_sec,
        "last_exercise": latest.get("exercise", "None"),
        "last_score": latest.get("score", 0),
        "stage": status.get("stage", latest.get("stage", "N/A")),
        "fps": status["fps"],
        "person_detected": status["person_detected"],
        "camera_connected": status["camera_connected"],
        "angles": status.get("angles", {"knee": 0, "hip": 0, "shoulder": 0}),
        "live_score": status.get("score", 0),
        "model_running": engine is not None
    })


def generate_frames():
    """Continuous MJPEG stream from the FitnessEngine."""
    import time
    while True:
        if engine:
            try:
                frame_bytes = engine.get_frame()
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
            except Exception as e:
                print(f"Frame generation error: {e}")
                time.sleep(0.1)
        else:
            # Produce a placeholder JPEG so the <img> tag doesn't error
            import numpy as np
            import cv2
            blank = np.zeros((480, 640, 3), dtype=np.uint8)
            cv2.putText(blank, "Camera Engine Offline", (80, 240),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255, 255, 255), 2)
            _, jpeg = cv2.imencode('.jpg', blank)
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + jpeg.tobytes() + b'\r\n')
            time.sleep(1)

@app.route('/video_feed')
def video_feed():
    """MJPEG video stream — no auth required (browser img tag can't send cookies)."""
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/export/json')
@login_required
def export_json():
    return send_file(DATA_FILE, as_attachment=True, download_name='workout_session.json')

@app.route('/export/csv')
@login_required
def export_csv():
    data = read_data()
    si = io.StringIO()
    cw = csv.writer(si)
    cw.writerow(['Time', 'Exercise', 'Reps', 'Score', 'Stage'])
    for d in data:
        cw.writerow([d.get('time'), d.get('exercise'), d.get('reps'), d.get('score'), d.get('stage')])
    output = io.BytesIO()
    output.write(si.getvalue().encode('utf-8'))
    output.seek(0)
    return send_file(output, as_attachment=True, download_name='workout_session.csv', mimetype='text/csv')


from logger import get_logger, reset_logger, SESSION_DIR
from evaluator import SessionEvaluator

@app.route("/session/current/evaluate", methods=["POST"])
@login_required
def evaluate_current():
    logger = get_logger()
    session_id = logger.get_session_id()
    evaluator = SessionEvaluator(session_id, logger.current_session_path)
    metrics = evaluator.evaluate()

    if metrics and user_id:
        conn = get_db_connection()
        try:
            data = read_data()
            start_time = data[0]["time"] if data else str(datetime.now())
            conn.execute(
                "INSERT OR REPLACE INTO Sessions (session_id, user_id, start_time, end_time, total_reps, avg_score) VALUES (?, ?, ?, ?, ?, ?)",
                (session_id, user_id, start_time, str(datetime.now()),
                 metrics.get("total_reps", 0), int(metrics.get("avg_accuracy", 0) * 100))
            )
            conn.commit()
        except Exception as e:
            print(f"Error saving session to DB: {e}")
        finally:
            conn.close()
    elif not metrics:
        print(f"Warning: No metrics generated for session {session_id} (empty session)")

    reset_logger()
    return jsonify({"session_id": session_id, "metrics": metrics})

@app.route("/session/<session_id>/metrics", methods=["GET"])
@login_required
def get_session_metrics(session_id):
    path = os.path.join(SESSION_DIR, f"session_{session_id}", "metrics.json")
    if os.path.exists(path):
        with open(path, "r") as f:
            return jsonify(json.load(f))
    return jsonify({"error": "Session not found"}), 404

@app.route("/session/<session_id>/image/<name>", methods=["GET"])
@login_required
def get_session_image(session_id, name):
    path = os.path.join(SESSION_DIR, f"session_{session_id}", f"{name}.png")
    if os.path.exists(path):
        return send_file(path, mimetype='image/png')
    return "Image not found", 404

@app.route("/sessions", methods=["GET"])
@login_required
def list_sessions():
    user_id = session.get("user_id")
    conn = get_db_connection()
    sessions = conn.execute(
        "SELECT * FROM Sessions WHERE user_id = ? ORDER BY start_time DESC",
        (user_id,)
    ).fetchall()
    conn.close()
    return jsonify([dict(s) for s in sessions])

@app.route("/session/<session_id>", methods=["DELETE"])
@login_required
def delete_session(session_id):
    user_id = session.get("user_id")
    conn = get_db_connection()
    conn.execute("DELETE FROM Sessions WHERE session_id = ? AND user_id = ?", (session_id, user_id))
    conn.commit()
    conn.close()
    
    # Optionally delete the folder too
    import shutil
    path = os.path.join(SESSION_DIR, f"session_{session_id}")
    if os.path.exists(path):
        shutil.rmtree(path)
        
    return jsonify({"message": "Session deleted"})

# Serve the frontend (same-origin avoids cross-origin cookie issues)
@app.route("/", methods=["GET"])
def serve_frontend():
    return send_file(os.path.join(FRONTEND_DIR, "index.html"))

@app.route("/health", methods=["GET"])
def health_check():
    return jsonify({
        "status": "online",
        "message": "AI Fitness API is running",
        "authenticated": "user_id" in session,
        "engine_running": engine is not None
    })

if __name__ == "__main__":
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    os.makedirs(SESSION_DIR, exist_ok=True)
    # use_reloader=False is critical — the reloader spawns a child process with a
    # different in-memory state, which makes cookie-based sessions unreliable during
    # development (each request may hit a different process instance).
    app.run(debug=True, host="0.0.0.0", port=5000, threaded=True, use_reloader=False)