import json
import os
import time
from datetime import datetime

# Base path relative to this file
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SESSION_DIR = os.path.join(BASE_DIR, "data/sessions")

class SessionLogger:
    def __init__(self):
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.current_session_path = os.path.join(SESSION_DIR, f"session_{self.session_id}")
        os.makedirs(self.current_session_path, exist_ok=True)
        self.events_file = os.path.join(self.current_session_path, "events.json")
        self.events = []

    def log_event(self, exercise, reps, score, stage, form_label_pred=None, form_label_true=None):
        event = {
            "time": str(datetime.now()),
            "exercise": exercise,
            "reps": reps,
            "score": score,
            "stage": stage,
            "form_label_pred": form_label_pred if form_label_pred is not None else (1 if score >= 80 else 0),
            "form_label_true": form_label_true if form_label_true is not None else (1 if score >= 75 else 0) # Mock true label
        }
        self.events.append(event)
        
        with open(self.events_file, "w") as f:
            json.dump(self.events, f, indent=4)
            
        # Also maintain compatibility with the legacy log for the live dashboard
        legacy_log = os.path.join(BASE_DIR, "data/workout.json")
        try:
            with open(legacy_log, "w") as f:
                json.dump(self.events, f, indent=4)
        except:
            pass

    def get_session_id(self):
        return self.session_id

# Global logger instance for the session
_current_logger = None

def get_logger():
    global _current_logger
    if _current_logger is None:
        _current_logger = SessionLogger()
    return _current_logger

def reset_logger():
    global _current_logger
    _current_logger = SessionLogger()
    return _current_logger

def log_data(data_entry):
    """Legacy compatibility wrapper."""
    logger = get_logger()
    logger.log_event(
        data_entry.get("exercise", "None"),
        data_entry.get("reps", 0),
        data_entry.get("score", 0),
        data_entry.get("stage", "N/A")
    )
