import sys
import os

# Add local path to import
sys.path.append(os.path.dirname(__file__))

import database as db
from ml_engine import ml_engine
import recommendation as rec_engine

def run_tests():
    print("--- STARTING AURAWELLNESS INTEGRATION TESTS ---")
    
    # 1. Database Init Test
    print("[TEST 1/5] Initializing Database Schema...")
    db.init_db()
    if not os.path.exists(db.DATABASE_NAME):
        print("❌ FAILED: Database file was not created!")
        return False
    print("✅ SUCCESS: Database file created.")

    # 2. ML Engine Training and Prediction Test
    print("[TEST 2/5] Training Scikit-Learn Fitness Models...")
    try:
        ml_engine.train()
        print("✅ SUCCESS: Models trained on synthetic coaching data.")
        
        print("[TEST 3/5] Testing ML Predictions...")
        pred = ml_engine.predict_wellness_targets(
            age=25,
            gender_str="Male",
            height=180.0,
            weight=75.0,
            activity_str="Moderately Active (3-5 days/week)",
            goal_str="Muscle Building"
        )
        print(f"Prediction Result: {pred}")
        
        required_keys = ["calories", "macro_split", "protein_g", "carb_g", "fat_g", "workout_archetype"]
        for key in required_keys:
            if key not in pred:
                print(f"❌ FAILED: Key '{key}' missing from ML predictions!")
                return False
        print("✅ SUCCESS: ML predictions successfully calculated and formatted.")
    except Exception as e:
        print(f"❌ FAILED: ML engine error: {e}")
        return False

    # 3. Database Write & Read Profile Test
    print("[TEST 4/5] Testing Database Profile Storage...")
    try:
        test_profile = {
            "name": "Integration Tester",
            "age": 30,
            "gender": "Female",
            "height": 165.0,
            "weight": 60.0,
            "activity_level": "Lightly Active (1-3 days/week)",
            "goal": "Weight Loss",
            "routine": "Sitting at a desk, walking in evenings.",
            "bmi": 22.0,
            "bmi_category": "Normal",
            "calorie_target": pred["calories"],
            "protein_target": pred["protein_g"],
            "carb_target": pred["carb_g"],
            "fat_target": pred["fat_g"],
            "workout_archetype": pred["workout_archetype"]
        }
        
        db.save_profile(test_profile)
        retrieved_profile = db.get_profile()
        
        if not retrieved_profile or retrieved_profile["name"] != "Integration Tester":
            print("❌ FAILED: Profile save/retrieve mismatch!")
            return False
        print("✅ SUCCESS: User profile successfully persisted and retrieved.")
    except Exception as e:
        print(f"❌ FAILED: Profile database operations error: {e}")
        return False

    # 4. Daily Log Log and Recommendations Test
    print("[TEST 5/5] Testing Daily Habit Logs & AI Recommendations...")
    try:
        log_date = "2026-08-04"
        test_log = {
            "water_intake": 1.5,
            "steps": 5000,
            "distance": 3.75,
            "exercise_type": "Yoga",
            "exercise_duration": 20,
            "exercise_sessions": 1,
            "breakfast": "Oats",
            "lunch": "Salad",
            "dinner": "Soup",
            "snacks": "Nuts",
            "sleep_duration": 6.0,
            "calories_consumed": 1400.0,
            "daily_activity": "Active morning stretch."
        }
        
        db.save_daily_log(log_date, test_log)
        retrieved_log = db.get_daily_log(log_date)
        
        if not retrieved_log or retrieved_log["steps"] != 5000:
            print("❌ FAILED: Daily log save/retrieve mismatch!")
            return False
            
        # Generate recommendations
        recs = rec_engine.generate_recommendations(retrieved_profile, retrieved_log)
        print(f"Generated {len(recs)} recommendation messages.")
        if len(recs) == 0:
            print("❌ FAILED: AI recommendation generator returned 0 suggestions.")
            return False
            
        print("✅ SUCCESS: Daily logs saved and AI advice pipeline functioning.")
    except Exception as e:
        print(f"❌ FAILED: Habit logger / AI advisor operations error: {e}")
        return False

    # Cleanup test tables/records
    print("Cleaning up database files after integration run...")
    try:
        conn = db.get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM user_profile")
        cursor.execute("DELETE FROM daily_logs")
        conn.commit()
        conn.close()
        print("🧹 Database cleanup complete.")
    except Exception as e:
        print(f"⚠️ Cleanup warning: {e}")

    print("\n🎉 ALL TESTS PASSED SUCCESSFULLY! AuraWellness system ready.")
    return True

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
