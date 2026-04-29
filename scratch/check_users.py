import sqlite3
import os

BASE_DIR = r"c:\Users\ayush\OneDrive\Documents\Pictures\Documents\exercise-ai-system"
DB_PATH = os.path.join(BASE_DIR, "data", "fitness.db")

def check_users():
    if not os.path.exists(DB_PATH):
        print("DB does not exist")
        return
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT name, email FROM Users")
    users = cursor.fetchall()
    print(f"Users found: {users}")
    conn.close()

if __name__ == "__main__":
    check_users()
