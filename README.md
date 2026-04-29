<<<<<<< HEAD
# 🏋️‍♂️ AI Fitness Monitoring System (NeuronFit)

An AI-powered fitness monitoring application that uses computer vision to track exercises, count repetitions, and provide real-time feedback on form and accuracy.

## 🚀 Overview
This project leverages **MediaPipe** for pose estimation and **Flask** for the backend to create a seamless workout experience. It detects exercises like squats, tracks joint angles (knee, hip, shoulder), and evaluates your performance in real-time.

---

## ✨ Features
- **Real-Time Pose Tracking**: High-precision skeleton tracking using MediaPipe Pose.
- **Automatic Exercise Detection**: Automatically identifies the exercise being performed.
- **Repetition Counter**: Accurate rep counting with state management (e.g., Up/Down detection).
- **Form Evaluation**: Calculates a "Form Score" based on biomechanical joint angles.
- **Web Dashboard**: Modern UI to view live video feed, metrics, and progress.
- **User Management**: Secure signup/login system with encrypted passwords.
- **Data Export**: Download your workout session data in JSON or CSV format.
- **Session History**: (Optional) View past session metrics and performance charts.

---

## 📁 Project Structure
```text
exercise-ai-system/
├── src/                # Backend Source Code
│   ├── api.py          # 🚀 Main Entry Point (Flask API & Web Server)
│   ├── engine.py       # Camera & AI Processing Engine
│   ├── pose.py         # MediaPipe Pose Estimation wrapper
│   ├── angles.py       # Geometric joint angle calculations
│   ├── movement.py     # Exercise detection logic
│   ├── rep_counter.py  # Logic for counting reps
│   ├── scoring.py      # Form accuracy calculation
│   ├── auth.py         # User Authentication (Bcrypt)
│   ├── db.py           # Database management (SQLite)
│   └── logger.py       # Workout data logging
├── Frontend/           # Web Interface
│   └── index.html      # Single-page application dashboard
├── data/               # Persistent Data
│   ├── fitness.db      # SQLite Database
│   └── workout.json    # Latest workout logs
└── requirements.txt    # Python dependencies
```

---

## 🛠️ Setup Instructions

### 1. Prerequisites
- **Python 3.10 or higher**
- A working **Webcam**

### 2. Environment Setup
Clone the repository and create a virtual environment:
```powershell
# Create virtual environment
python -m venv env

# Activate virtual environment
.\env\Scripts\activate
```

### 3. Install Dependencies
```powershell
pip install -r requirements.txt
```

---

## 🏃‍♂️ How to Run

### **Option 1: Full Web Application (Recommended)**
This starts the backend API and serves the dashboard UI.
```powershell
python src/api.py
```
- Open your browser and go to: `http://localhost:5000`
- Sign up or log in to access the dashboard.

### **Option 2: Standalone Camera Monitor**
Run the AI engine directly with an OpenCV window (no web UI).
```powershell
python src/main.py
```

---

## 🎯 Getting Started (Entry Point)
To start using the full system, always begin with **`src/api.py`**. This file initializes the database, starts the AI camera engine, and hosts the web interface where all metrics are displayed.

---

## 🛠️ Technology Stack
- **Backend**: Flask (Python)
- **AI/CV**: MediaPipe, OpenCV
- **Database**: SQLite
- **Security**: Bcrypt (Password Hashing)
- **Frontend**: HTML5, Vanilla CSS, JavaScript
=======
# exercise-system
>>>>>>> 6d0f6745ceffac733618fcc4adcdad2fea7036c6
