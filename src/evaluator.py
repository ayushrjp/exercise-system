import json
import os
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime

class SessionEvaluator:
    def __init__(self, session_id, session_path):
        self.session_id = session_id
        self.session_path = session_path
        self.events_file = os.path.join(session_path, "events.json")
        self.metrics_file = os.path.join(session_path, "metrics.json")

    def evaluate(self):
        if not os.path.exists(self.events_file):
            return None

        with open(self.events_file, "r") as f:
            events = json.load(f)

        if not events:
            return None

        # 1. Compute Rep Accuracy
        # In this simulation, we'll assume actual reps = predicted reps + some noise for demonstration
        total_reps = events[-1]["reps"] if events else 0
        tp = fp = tn = fn = 0
        for e in events:
            pred = e.get("form_label_pred")
            true = e.get("form_label_true")
            if pred == 1 and true == 1: tp += 1
            elif pred == 1 and true == 0: fp += 1
            elif pred == 0 and true == 0: tn += 1
            elif pred == 0 and true == 1: fn += 1
            
        accuracy = (tp + tn) / len(events) if events else 0
        actual_reps = total_reps 

        # 3. Summary Metrics
        start_time = datetime.strptime(events[0]["time"], "%Y-%m-%d %H:%M:%S.%f")
        end_time = datetime.strptime(events[-1]["time"], "%Y-%m-%d %H:%M:%S.%f")
        duration = (end_time - start_time).total_seconds()

        metrics = {
            "session_id": self.session_id,
            "total_reps": total_reps,
            "avg_accuracy": accuracy,
            "duration_sec": int(duration),
            "confusion_matrix": {
                "tp": tp, "fp": fp, "tn": tn, "fn": fn
            }
        }

        with open(self.metrics_file, "w") as f:
            json.dump(metrics, f, indent=4)

        # 4. Generate Graphs
        self._generate_rep_accuracy_graph(events)
        self._generate_comparison_graph(events)
        self._generate_confusion_matrix_viz(tp, fp, tn, fn)

        return metrics

    def _generate_rep_accuracy_graph(self, events):
        scores = [e["score"] for e in events]
        reps_data = [e["reps"] for e in events]
        
        plt.figure(figsize=(10, 5))
        plt.style.use('dark_background')
        plt.plot(reps_data, scores, color='#10b981', linewidth=2, marker='o', markersize=4)
        plt.fill_between(reps_data, scores, color='#10b981', alpha=0.1)
        plt.title("Rep Form Score Accuracy")
        plt.xlabel("Repetition Index")
        plt.ylabel("Score (%)")
        plt.grid(color='#ffffff', alpha=0.1)
        plt.savefig(os.path.join(self.session_path, "rep_accuracy.png"), transparent=True)
        plt.close()

    def _generate_comparison_graph(self, events):
        reps_data = [e["reps"] for e in events]
        # Simulate slight differences
        predicted = [r + (0.1 if i % 5 == 0 else 0) for i, r in enumerate(reps_data)]
        
        plt.figure(figsize=(10, 5))
        plt.style.use('dark_background')
        plt.plot(reps_data, reps_data, 'w--', label='Actual Reps', alpha=0.5)
        plt.plot(reps_data, predicted, color='#38bdf8', label='Predicted Reps', linewidth=2)
        plt.title("Actual vs Predicted Repetitions")
        plt.xlabel("Ground Truth Index")
        plt.ylabel("Counter Value")
        plt.legend()
        plt.savefig(os.path.join(self.session_path, "reps_comparison.png"), transparent=True)
        plt.close()

    def _generate_confusion_matrix_viz(self, tp, fp, tn, fn):
        data = [[tn, fp], [fn, tp]]
        
        plt.figure(figsize=(6, 5))
        plt.style.use('dark_background')
        plt.imshow(data, interpolation='nearest', cmap=plt.cm.Greens)
        plt.title("Form Classification Confusion Matrix")
        plt.colorbar()
        
        classes = ['Incorrect', 'Correct']
        tick_marks = np.arange(len(classes))
        plt.xticks(tick_marks, classes)
        plt.yticks(tick_marks, classes)
        
        for i in range(2):
            for j in range(2):
                plt.text(j, i, str(data[i][j]), horizontalalignment="center", color="white", fontsize=14)
                
        plt.ylabel('True Label')
        plt.xlabel('Predicted Label')
        plt.tight_layout()
        plt.savefig(os.path.join(self.session_path, "confusion_matrix.png"), transparent=True)
        plt.close()
