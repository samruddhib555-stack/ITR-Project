import sqlite3
import os
from datetime import datetime

DATABASE_NAME = "aura_wellness.db"

def get_connection():
    """Returns a connection to the SQLite database."""
    conn = sqlite3.connect(DATABASE_NAME)
    conn.row_factory = sqlite3.Row  # Access columns by name
    return conn

def init_db():
    """Initializes the database schema if tables do not exist."""
    conn = get_connection()
    cursor = conn.cursor()
    
    # User Profile Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_profile (
            id INTEGER PRIMARY KEY CHECK (id = 1),
            name TEXT NOT NULL,
            age INTEGER NOT NULL,
            gender TEXT NOT NULL,
            height REAL NOT NULL,
            weight REAL NOT NULL,
            activity_level TEXT NOT NULL,
            goal TEXT NOT NULL,
            routine TEXT,
            bmi REAL NOT NULL,
            bmi_category TEXT NOT NULL,
            calorie_target REAL,
            macro_split TEXT,
            protein_target REAL,
            carb_target REAL,
            fat_target REAL,
            workout_archetype TEXT,
            created_at TEXT NOT NULL
        )
    """)

    # Migrate: add macro_split column if it doesn't exist (for existing databases)
    try:
        cursor.execute("ALTER TABLE user_profile ADD COLUMN macro_split TEXT")
        conn.commit()
    except Exception:
        pass  # Column already exists
    
    # Daily Tracking Logs Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS daily_logs (
            log_date TEXT PRIMARY KEY, -- YYYY-MM-DD
            water_intake REAL DEFAULT 0.0, -- in Litres
            steps INTEGER DEFAULT 0,
            distance REAL DEFAULT 0.0, -- in km
            exercise_type TEXT,
            exercise_duration INTEGER DEFAULT 0, -- in minutes
            exercise_sessions INTEGER DEFAULT 0,
            breakfast TEXT,
            lunch TEXT,
            dinner TEXT,
            snacks TEXT,
            sleep_duration REAL DEFAULT 0.0, -- in hours
            calories_consumed REAL DEFAULT 0.0,
            daily_activity TEXT,
            saved_at TEXT NOT NULL
        )
    """)
    
    conn.commit()
    conn.close()

def save_profile(profile_data):
    """
    Saves or updates the user profile.
    profile_data is a dictionary with keys matching the schema.
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    # Insert or Replace logic for ID = 1
    cursor.execute("""
        INSERT OR REPLACE INTO user_profile (
            id, name, age, gender, height, weight, activity_level, goal, routine,
            bmi, bmi_category, calorie_target, macro_split, protein_target, carb_target, fat_target,
            workout_archetype, created_at
        ) VALUES (
            1, :name, :age, :gender, :height, :weight, :activity_level, :goal, :routine,
            :bmi, :bmi_category, :calorie_target, :macro_split, :protein_target, :carb_target, :fat_target,
            :workout_archetype, :created_at
        )
    """, {
        **profile_data,
        "macro_split": profile_data.get("macro_split", "Balanced"),
        "created_at": datetime.now().isoformat()
    })
    
    conn.commit()
    conn.close()

def get_profile():
    """Retrieves the user profile dictionary or None if it doesn't exist."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM user_profile WHERE id = 1")
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return dict(row)
    return None

def save_daily_log(log_date, log_data):
    """
    Saves or updates the daily wellness metrics for a given date.
    log_date format: YYYY-MM-DD
    log_data is a dictionary with matching keys.
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT OR REPLACE INTO daily_logs (
            log_date, water_intake, steps, distance, exercise_type, 
            exercise_duration, exercise_sessions, breakfast, lunch, 
            dinner, snacks, sleep_duration, calories_consumed, daily_activity, saved_at
        ) VALUES (
            :log_date, :water_intake, :steps, :distance, :exercise_type,
            :exercise_duration, :exercise_sessions, :breakfast, :lunch,
            :dinner, :snacks, :sleep_duration, :calories_consumed, :daily_activity, :saved_at
        )
    """, {
        "log_date": log_date,
        "water_intake": log_data.get("water_intake", 0.0),
        "steps": log_data.get("steps", 0),
        "distance": log_data.get("distance", 0.0),
        "exercise_type": log_data.get("exercise_type", ""),
        "exercise_duration": log_data.get("exercise_duration", 0),
        "exercise_sessions": log_data.get("exercise_sessions", 0),
        "breakfast": log_data.get("breakfast", ""),
        "lunch": log_data.get("lunch", ""),
        "dinner": log_data.get("dinner", ""),
        "snacks": log_data.get("snacks", ""),
        "sleep_duration": log_data.get("sleep_duration", 0.0),
        "calories_consumed": log_data.get("calories_consumed", 0.0),
        "daily_activity": log_data.get("daily_activity", ""),
        "saved_at": datetime.now().isoformat()
    })
    
    conn.commit()
    conn.close()

def get_daily_log(log_date):
    """Retrieves the daily log for a given date or a default empty log dictionary."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM daily_logs WHERE log_date = ?", (log_date,))
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return dict(row)
        
    return {
        "log_date": log_date,
        "water_intake": 0.0,
        "steps": 0,
        "distance": 0.0,
        "exercise_type": "",
        "exercise_duration": 0,
        "exercise_sessions": 0,
        "breakfast": "",
        "lunch": "",
        "dinner": "",
        "snacks": "",
        "sleep_duration": 0.0,
        "calories_consumed": 0.0,
        "daily_activity": ""
    }

def get_all_daily_logs():
    """Retrieves all daily logs sorted by date ascending."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM daily_logs ORDER BY log_date ASC")
    rows = cursor.fetchall()
    conn.close()
    
    return [dict(r) for r in rows]

# Initialize tables automatically when this script is imported
init_db()
