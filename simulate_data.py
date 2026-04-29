import json
import time
import os
from datetime import datetime
import random

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE_DIR, "data/workout.json")

def simulate():
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    data = []
    
    print(f"Simulating data into {DATA_FILE}")
    for i in range(1, 16):
        entry = {
            "time": str(datetime.now()),
            "exercise": "squat",
            "reps": i,
            "score": random.randint(85, 98),
            "stage": "up" if i % 2 == 0 else "down"
        }
        data.append(entry)
        
        with open(DATA_FILE, "w") as f:
            json.dump(data, f, indent=4)
            
        print(f"Logged rep {i}")
        # time.sleep(2) # Remove sleep for faster execution

if __name__ == "__main__":
    simulate()
