import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.tree import DecisionTreeClassifier
import pickle
import os

# Mapping definitions
GENDER_MAP = {"Male": 0, "Female": 1}
ACTIVITY_MAP = {
    "Sedentary (Little to no exercise)": 0,
    "Lightly Active (1-3 days/week)": 1,
    "Moderately Active (3-5 days/week)": 2,
    "Very Active (6-7 days/week)": 3
}
GOAL_MAP = {
    "Weight Loss": 0,
    "Weight Gain": 1,
    "Muscle Building": 2,
    "General Fitness": 3,
    "Improve Health / Lifestyle": 4
}

class AuraMLEngine:
    def __init__(self):
        self.calorie_model = None
        self.macro_model = None
        self.archetype_model = None
        self.is_trained = False
        
    def generate_synthetic_data(self, n_samples=1500):
        """Generates synthetic coaching data representing sports nutrition rules with realistic variance."""
        np.random.seed(42)
        
        # Features
        age = np.random.randint(18, 76, size=n_samples)
        gender = np.random.randint(0, 2, size=n_samples)
        height = np.random.randint(145, 201, size=n_samples)
        
        # Weight linked loosely to height for BMI realism
        bmi = np.random.normal(25, 4.5, size=n_samples)
        weight = bmi * ((height / 100.0) ** 2)
        
        activity = np.random.randint(0, 4, size=n_samples)
        goal = np.random.randint(0, 5, size=n_samples)
        
        # Calculate Base Calorie Targets (Harris-Benedict formula + offsets)
        calories = []
        macro_labels = []
        archetypes = []
        
        activity_multipliers = [1.2, 1.375, 1.55, 1.725]
        
        for i in range(n_samples):
            # Mifflin-St Jeor Equation
            if gender[i] == 0:  # Male
                bmr = 10 * weight[i] + 6.25 * height[i] - 5 * age[i] + 5
            else:  # Female
                bmr = 10 * weight[i] + 6.25 * height[i] - 5 * age[i] - 161
                
            tdee = bmr * activity_multipliers[activity[i]]
            
            # Goal offsets
            g = goal[i]
            if g == 0:  # Weight Loss
                target_cal = tdee - 500
                # Lower limit safety
                target_cal = max(target_cal, 1200 if gender[i] == 1 else 1500)
            elif g == 1:  # Weight Gain
                target_cal = tdee + 400
            elif g == 2:  # Muscle Building
                target_cal = tdee + 250
            else:  # Maintenance
                target_cal = tdee
                
            # Add Gaussian noise for realistic ML training (std = 75 calories)
            target_cal += np.random.normal(0, 75)
            calories.append(round(target_cal))
            
            # Label Macro Split
            # Rules: Muscle Building/Weight Loss -> High Protein; Very Active -> High Carb; Health/Gain -> Balanced
            if g in [0, 2]:
                macro = "High Protein"
            elif activity[i] == 3:
                macro = "High Carb"
            else:
                macro = "Balanced"
                
            # Add 8% random label swap to simulate real world noise
            if np.random.rand() < 0.08:
                macro = np.random.choice(["High Protein", "High Carb", "Balanced"])
            macro_labels.append(macro)
            
            # Label Workout Archetype
            # Goal + Activity -> Split
            act = activity[i]
            if g == 2:  # Muscle Building
                arch = "Strength Training Split"
            elif g == 0 and act <= 1:
                arch = "Active Recovery & Yoga"
            elif act >= 2:
                arch = "Endurance & Cardio"
            else:
                arch = "Functional & Mobility"
                
            if np.random.rand() < 0.08:
                arch = np.random.choice(["Strength Training Split", "Endurance & Cardio", "Functional & Mobility", "Active Recovery & Yoga"])
            archetypes.append(arch)
            
        df = pd.DataFrame({
            "age": age,
            "gender": gender,
            "height": height,
            "weight": weight,
            "activity": activity,
            "goal": goal,
            "calories": calories,
            "macro_split": macro_labels,
            "archetype": archetypes
        })
        
        return df

    def train(self):
        """Trains Scikit-learn models on synthetic fitness dataset."""
        df = self.generate_synthetic_data()
        
        # Features and Targets
        X = df[["age", "gender", "height", "weight", "activity", "goal"]]
        y_cal = df["calories"]
        y_macro = df["macro_split"]
        y_arch = df["archetype"]
        
        # Calorie Regressor
        self.calorie_model = RandomForestRegressor(n_estimators=50, random_state=42)
        self.calorie_model.fit(X, y_cal)
        
        # Macro Split Classifier
        self.macro_model = DecisionTreeClassifier(max_depth=5, random_state=42)
        self.macro_model.fit(X, y_macro)
        
        # Workout Archetype Classifier
        self.archetype_model = DecisionTreeClassifier(max_depth=5, random_state=42)
        self.archetype_model.fit(X, y_arch)
        
        self.is_trained = True
        
    def predict_wellness_targets(self, age, gender_str, height, weight, activity_str, goal_str):
        """
        Predicts target calories, macronutrient split (in grams), and workout archetype.
        Inputs are string representations from the UI form.
        """
        if not self.is_trained:
            self.train()
            
        # Map strings to numerical features
        gender = GENDER_MAP.get(gender_str, 0)
        activity = ACTIVITY_MAP.get(activity_str, 0)
        goal = GOAL_MAP.get(goal_str, 3)
        
        X_pred = pd.DataFrame([[age, gender, height, weight, activity, goal]], 
                              columns=["age", "gender", "height", "weight", "activity", "goal"])
        
        # Predictions
        pred_calories = float(self.calorie_model.predict(X_pred)[0])
        pred_macro_split = str(self.macro_model.predict(X_pred)[0])
        pred_archetype = str(self.archetype_model.predict(X_pred)[0])
        
        # Calculate macro grams based on calories and split guidelines
        # Protein/Carbs: 4 kcal/g, Fat: 9 kcal/g
        if pred_macro_split == "High Protein":
            p_pct, c_pct, f_pct = 0.35, 0.35, 0.30
        elif pred_macro_split == "High Carb":
            p_pct, c_pct, f_pct = 0.15, 0.60, 0.25
        else: # Balanced
            p_pct, c_pct, f_pct = 0.25, 0.45, 0.30
            
        protein_g = round((pred_calories * p_pct) / 4.0)
        carb_g = round((pred_calories * c_pct) / 4.0)
        fat_g = round((pred_calories * f_pct) / 9.0)
        
        return {
            "calories": round(pred_calories),
            "macro_split": pred_macro_split,
            "protein_g": protein_g,
            "carb_g": carb_g,
            "fat_g": fat_g,
            "workout_archetype": pred_archetype
        }

# Global singleton
ml_engine = AuraMLEngine()
