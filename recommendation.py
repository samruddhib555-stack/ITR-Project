def get_hydration_target(weight_kg):
    """Calculates water target in Liters: weight * 0.035, clamped between 2.0 and 4.0L."""
    target = weight_kg * 0.035
    return round(max(2.0, min(target, 4.0)), 1)

def get_steps_target(activity_level):
    """Calculates target steps based on user activity level."""
    if "Sedentary" in activity_level:
        return 6000
    elif "Lightly" in activity_level:
        return 8000
    elif "Moderately" in activity_level:
        return 10000
    else:  # Very Active
        return 12000

def get_sleep_target():
    return 7.5

def get_exercise_target(archetype):
    """Calculates active minutes targets based on workout archetype."""
    if "Strength" in archetype:
        return 45
    elif "Endurance" in archetype:
        return 50
    elif "Functional" in archetype:
        return 35
    else:  # Active Recovery
        return 30

def generate_recommendations(profile, today_log):
    """
    Generates personalized recommendations based on profile targets and today's logged metrics.
    Ensures safe, wellness-focused guidance avoiding extreme diet or dangerous medical claims.
    """
    recs = []
    
    # Extract targets
    weight = profile.get("weight", 70.0)
    activity_level = profile.get("activity_level", "Moderately Active")
    archetype = profile.get("workout_archetype", "Balanced")
    goal = profile.get("goal", "General Fitness")
    calorie_target = profile.get("calorie_target", 2000.0)
    
    water_target = get_hydration_target(weight)
    steps_target = get_steps_target(activity_level)
    sleep_target = get_sleep_target()
    exercise_target = get_exercise_target(archetype)
    
    # 1. Hydration Recommendations
    water_logged = today_log.get("water_intake", 0.0)
    if water_logged == 0:
        recs.append({
            "category": "Hydration",
            "status": "warning",
            "message": f"You haven't logged any water today. Aim to drink about {water_target}L to support metabolic processes and muscle recovery."
        })
    elif water_logged < water_target:
        deficit = round(water_target - water_logged, 1)
        recs.append({
            "category": "Hydration",
            "status": "warning",
            "message": f"Your water intake is below target. You need {deficit}L more to hit your daily goal of {water_target}L. Try keeping a flask nearby."
        })
    else:
        recs.append({
            "category": "Hydration",
            "status": "success",
            "message": f"Excellent hydration! You hit your goal of {water_target}L. Proper hydration optimizes joint lubrication and cell nourishment."
        })
        
    # 2. Activity / Steps Recommendations
    steps_logged = today_log.get("steps", 0)
    if steps_logged == 0:
        recs.append({
            "category": "Activity",
            "status": "warning",
            "message": f"No steps logged yet. Start with a light 15-minute walk. Your personalized daily target is {steps_target:,} steps."
        })
    elif steps_logged < steps_target:
        deficit = steps_target - steps_logged
        pct = round((steps_logged / steps_target) * 100)
        recs.append({
            "category": "Activity",
            "status": "warning",
            "message": f"You're at {pct}% of your step goal. Walk {deficit:,} more steps to hit your {steps_target:,} target. Walking assists cardiovascular health."
        })
    else:
        recs.append({
            "category": "Activity",
            "status": "success",
            "message": f"Incredible activity levels! You achieved {steps_logged:,} steps, exceeding your {steps_target:,} target. This is fantastic for calorie burn and stamina."
        })

    # 3. Exercise Duration Recommendations
    exercise_duration = today_log.get("exercise_duration", 0)
    if exercise_duration == 0:
        recs.append({
            "category": "Exercise",
            "status": "warning",
            "message": f"No workouts logged today. For your '{archetype}' profile, a daily exercise session of {exercise_target} minutes is optimal."
        })
    elif exercise_duration < exercise_target:
        deficit = exercise_target - exercise_duration
        recs.append({
            "category": "Exercise",
            "status": "warning",
            "message": f"Today's workout session was {exercise_duration} minutes (target: {exercise_target}m). Try adding a quick {deficit}-minute stretch or core sequence to finish."
        })
    else:
        recs.append({
            "category": "Exercise",
            "status": "success",
            "message": f"Workout completed! You logged {exercise_duration} minutes of active exercise. Consistency with your '{archetype}' routine yields the best results."
        })

    # 4. Nutrition / Diet Recommendations
    calories_consumed = today_log.get("calories_consumed", 0.0)
    breakfast = today_log.get("breakfast", "")
    lunch = today_log.get("lunch", "")
    dinner = today_log.get("dinner", "")
    
    if calories_consumed == 0.0 and not (breakfast or lunch or dinner):
        recs.append({
            "category": "Nutrition",
            "status": "info",
            "message": "Remember to log your meals today to track your nutrition and ensure you are fueling your body adequately."
        })
    else:
        # Check calorie balance
        if calories_consumed > 0:
            diff = calories_consumed - calorie_target
            if abs(diff) <= 200:
                recs.append({
                    "category": "Nutrition",
                    "status": "success",
                    "message": f"You are right on track! Calorie intake ({round(calories_consumed)} kcal) is perfectly balanced with your goal target of {round(calorie_target)} kcal."
                })
            elif diff > 200:
                recs.append({
                    "category": "Nutrition",
                    "status": "warning",
                    "message": f"Today's calorie intake ({round(calories_consumed)} kcal) is higher than your goal target of {round(calorie_target)} kcal. Focus on high-volume, low-density foods (vegetables, lean protein) to stay full."
                })
            else: # deficit > 200
                recs.append({
                    "category": "Nutrition",
                    "status": "info",
                    "message": f"You are in a calorie deficit ({round(calories_consumed)} logged vs {round(calorie_target)} target). Ensure you are eating enough dense, nutritious food to maintain energy levels."
                })
                
        # Goal-specific food suggestions
        if goal == "Muscle Building" or goal == "Weight Loss":
            recs.append({
                "category": "Nutrition",
                "status": "info",
                "message": "Try adding more protein-rich foods (lean chicken, fish, tofu, lentils, or eggs) to support muscle recovery and boost satiety."
            })
        elif goal == "Weight Gain":
            recs.append({
                "category": "Nutrition",
                "status": "info",
                "message": "Incorporate healthy fats (avocados, nuts, olive oil, seeds) to pack nutrient-dense calories into your meals without feeling overly full."
            })
        else: # General Fitness or Improve Health
            recs.append({
                "category": "Nutrition",
                "status": "info",
                "message": "Focus on whole grains, colorful vegetables, and essential fatty acids (Omega-3s) to promote cardiovascular health and reduce inflammation."
            })

    # 5. Sleep Recommendations
    sleep_logged = today_log.get("sleep_duration", 0.0)
    if sleep_logged == 0:
        recs.append({
            "category": "Sleep",
            "status": "warning",
            "message": f"Sleep log is empty. Aim for {sleep_target} hours of sleep tonight. Sleep is crucial for muscle protein synthesis and mental clarity."
        })
    elif sleep_logged < sleep_target:
        deficit = round(sleep_target - sleep_logged, 1)
        recs.append({
            "category": "Sleep",
            "status": "warning",
            "message": f"You got {sleep_logged} hours of sleep (target: {sleep_target}h). Sleep debt can impact hormone balance. Try an early wind-down routine tonight."
        })
    else:
        recs.append({
            "category": "Sleep",
            "status": "success",
            "message": f"Fantastic sleep! You got {sleep_logged} hours of rest. Quality rest is when your body rebuilds tissues and resets energy systems."
        })

    return recs
