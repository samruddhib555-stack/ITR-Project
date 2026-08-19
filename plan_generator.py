"""
plan_generator.py
Auto-generates personalized Diet Plan, Workout Plan, Hydration Schedule,
and Daily Routine based on the user's AuraWellness profile.
"""

import random

# ─── FOOD DATABASES ────────────────────────────────────────────────────────────

BREAKFAST_DB = {
    "Weight Loss": [
        {"name": "Greek Yogurt Bowl", "desc": "Low-fat Greek yogurt, blueberries, chia seeds & honey drizzle", "protein": 20, "carbs": 28, "fat": 4, "cal_factor": 0.22},
        {"name": "Veggie Omelette", "desc": "3-egg omelette with spinach, bell peppers, mushrooms & feta", "protein": 24, "carbs": 8, "fat": 14, "cal_factor": 0.22},
        {"name": "Overnight Oats", "desc": "Rolled oats, almond milk, banana slices & flaxseeds", "protein": 12, "carbs": 45, "fat": 6, "cal_factor": 0.22},
        {"name": "Avocado Toast", "desc": "Whole grain toast, mashed avocado, poached egg & cherry tomatoes", "protein": 16, "carbs": 30, "fat": 18, "cal_factor": 0.22},
    ],
    "Muscle Building": [
        {"name": "Protein Pancakes", "desc": "Oat-banana pancakes with whey protein, peanut butter & maple syrup", "protein": 38, "carbs": 55, "fat": 12, "cal_factor": 0.25},
        {"name": "Scrambled Eggs & Salmon", "desc": "4 whole eggs scrambled with smoked salmon, avocado & whole grain toast", "protein": 42, "carbs": 32, "fat": 22, "cal_factor": 0.25},
        {"name": "Mass Smoothie Bowl", "desc": "Banana, oats, whey protein, almond butter & granola topping", "protein": 35, "carbs": 68, "fat": 14, "cal_factor": 0.25},
        {"name": "Cottage Cheese Bowl", "desc": "Full-fat cottage cheese, walnuts, berries & protein granola", "protein": 30, "carbs": 38, "fat": 16, "cal_factor": 0.25},
    ],
    "General Fitness": [
        {"name": "Muesli & Fruit Bowl", "desc": "Swiss muesli, seasonal fruits, almond milk & mixed seeds", "protein": 14, "carbs": 52, "fat": 8, "cal_factor": 0.23},
        {"name": "Egg & Veggie Toast", "desc": "2 eggs any style, whole grain toast, cucumber & tomato salad", "protein": 18, "carbs": 35, "fat": 12, "cal_factor": 0.23},
        {"name": "Smoothie & Nuts", "desc": "Spinach-mango-banana smoothie with a handful of mixed nuts", "protein": 10, "carbs": 48, "fat": 14, "cal_factor": 0.23},
    ],
    "Weight Gain": [
        {"name": "Big Breakfast Plate", "desc": "4 eggs, whole wheat toast, baked beans, avocado & orange juice", "protein": 36, "carbs": 72, "fat": 24, "cal_factor": 0.28},
        {"name": "Peanut Butter Oatmeal", "desc": "Steel-cut oats, 2 tbsp peanut butter, banana, honey & whole milk", "protein": 22, "carbs": 80, "fat": 20, "cal_factor": 0.28},
        {"name": "Bagel & Cream Cheese", "desc": "Everything bagel, cream cheese, smoked salmon & capers", "protein": 28, "carbs": 65, "fat": 22, "cal_factor": 0.28},
    ],
    "Improve Health / Lifestyle": [
        {"name": "Anti-Inflammatory Bowl", "desc": "Turmeric oats, ginger, flaxseeds, blueberries & walnut pieces", "protein": 12, "carbs": 44, "fat": 10, "cal_factor": 0.23},
        {"name": "Poached Egg Platter", "desc": "2 poached eggs, wilted spinach, roasted tomatoes & whole grain toast", "protein": 18, "carbs": 30, "fat": 10, "cal_factor": 0.23},
        {"name": "Green Smoothie", "desc": "Kale, cucumber, green apple, ginger, lemon & hemp seeds", "protein": 8, "carbs": 38, "fat": 5, "cal_factor": 0.23},
    ]
}

LUNCH_DB = {
    "Weight Loss": [
        {"name": "Grilled Chicken Salad", "desc": "150g grilled chicken breast, mixed greens, cherry tomatoes, cucumber, olive oil & lemon dressing", "protein": 38, "carbs": 15, "fat": 10, "cal_factor": 0.32},
        {"name": "Lentil Soup & Rye Bread", "desc": "Hearty red lentil & vegetable soup with 1 slice rye bread & side salad", "protein": 22, "carbs": 48, "fat": 5, "cal_factor": 0.32},
        {"name": "Tuna Wrap", "desc": "Whole wheat wrap, canned tuna, lettuce, tomato, low-fat mayo & lemon zest", "protein": 32, "carbs": 40, "fat": 8, "cal_factor": 0.32},
        {"name": "Quinoa Veggie Bowl", "desc": "Cooked quinoa, roasted vegetables, hummus, feta cheese & lemon tahini", "protein": 18, "carbs": 52, "fat": 12, "cal_factor": 0.32},
    ],
    "Muscle Building": [
        {"name": "Chicken & Rice Bowl", "desc": "200g grilled chicken breast, 1 cup brown rice, broccoli & teriyaki glaze", "protein": 52, "carbs": 75, "fat": 8, "cal_factor": 0.35},
        {"name": "Beef Stir-Fry", "desc": "Lean beef strips, mixed vegetables, brown rice & soy-ginger sauce", "protein": 45, "carbs": 65, "fat": 14, "cal_factor": 0.35},
        {"name": "Turkey & Sweet Potato", "desc": "Ground turkey, roasted sweet potato, spinach & olive oil", "protein": 48, "carbs": 60, "fat": 10, "cal_factor": 0.35},
        {"name": "Salmon Quinoa Bowl", "desc": "Baked salmon fillet, quinoa, edamame, avocado & sesame dressing", "protein": 50, "carbs": 55, "fat": 20, "cal_factor": 0.35},
    ],
    "General Fitness": [
        {"name": "Buddha Bowl", "desc": "Mixed grains, roasted chickpeas, greens, roasted veggies & tahini drizzle", "protein": 20, "carbs": 58, "fat": 14, "cal_factor": 0.33},
        {"name": "Chicken Wrap", "desc": "Whole wheat wrap, grilled chicken, avocado, lettuce & Greek yogurt dressing", "protein": 35, "carbs": 42, "fat": 12, "cal_factor": 0.33},
        {"name": "Pasta Primavera", "desc": "Whole wheat pasta, mixed vegetables, olive oil, garlic & parmesan", "protein": 18, "carbs": 68, "fat": 12, "cal_factor": 0.33},
    ],
    "Weight Gain": [
        {"name": "Pasta & Meatballs", "desc": "200g whole wheat pasta, beef meatballs, tomato sauce & parmesan", "protein": 48, "carbs": 90, "fat": 22, "cal_factor": 0.37},
        {"name": "Rice, Dal & Roti", "desc": "2 cups rice, protein-rich dal, 2 rotis & mixed pickle", "protein": 28, "carbs": 110, "fat": 10, "cal_factor": 0.37},
        {"name": "Loaded Chicken Burrito", "desc": "Large tortilla, chicken, rice, beans, cheese, guacamole & sour cream", "protein": 44, "carbs": 95, "fat": 26, "cal_factor": 0.37},
    ],
    "Improve Health / Lifestyle": [
        {"name": "Mediterranean Plate", "desc": "Grilled fish, tabbouleh, hummus, whole grain pita & olives", "protein": 30, "carbs": 45, "fat": 16, "cal_factor": 0.33},
        {"name": "Veggie Dal Bowl", "desc": "Mixed dal, brown rice, sautéed vegetables & low-fat yogurt", "protein": 20, "carbs": 60, "fat": 6, "cal_factor": 0.33},
        {"name": "Chicken & Avocado Salad", "desc": "Grilled chicken, avocado, mixed greens, nuts & lemon vinaigrette", "protein": 35, "carbs": 20, "fat": 18, "cal_factor": 0.33},
    ]
}

DINNER_DB = {
    "Weight Loss": [
        {"name": "Baked Salmon & Veggies", "desc": "150g salmon fillet, roasted asparagus, cherry tomatoes & lemon-dill sauce", "protein": 36, "carbs": 12, "fat": 14, "cal_factor": 0.30},
        {"name": "Chicken Stir-Fry", "desc": "120g chicken breast, broccoli, bell peppers, snap peas & light soy sauce (no rice)", "protein": 32, "carbs": 18, "fat": 8, "cal_factor": 0.30},
        {"name": "Cauliflower Dal Soup", "desc": "Spiced red lentil soup with cauliflower, ginger & coconut milk", "protein": 18, "carbs": 35, "fat": 6, "cal_factor": 0.30},
        {"name": "Grilled Fish Tacos", "desc": "2 corn tortillas, grilled white fish, cabbage slaw, salsa & lime", "protein": 28, "carbs": 38, "fat": 8, "cal_factor": 0.30},
    ],
    "Muscle Building": [
        {"name": "Steak & Potato", "desc": "200g sirloin steak, roasted sweet potato, sautéed greens & garlic butter", "protein": 55, "carbs": 55, "fat": 24, "cal_factor": 0.33},
        {"name": "Chicken Pasta", "desc": "Grilled chicken breast, whole wheat pasta, tomato sauce, spinach & cheese", "protein": 48, "carbs": 70, "fat": 14, "cal_factor": 0.33},
        {"name": "Salmon & Rice", "desc": "Baked salmon, brown rice, steamed broccoli & soy glaze", "protein": 50, "carbs": 60, "fat": 18, "cal_factor": 0.33},
        {"name": "Beef & Veggie Bowl", "desc": "Lean ground beef, roasted vegetables, quinoa & avocado", "protein": 52, "carbs": 55, "fat": 20, "cal_factor": 0.33},
    ],
    "General Fitness": [
        {"name": "Baked Cod & Quinoa", "desc": "Herb-baked cod, quinoa, steamed vegetables & lemon-caper sauce", "protein": 32, "carbs": 45, "fat": 8, "cal_factor": 0.30},
        {"name": "Tofu Curry", "desc": "Firm tofu, mixed vegetables in mild tomato-coconut curry, brown rice", "protein": 22, "carbs": 55, "fat": 12, "cal_factor": 0.30},
        {"name": "Turkey Meatballs", "desc": "Turkey meatballs, zucchini noodles, tomato sauce & basil", "protein": 38, "carbs": 28, "fat": 12, "cal_factor": 0.30},
    ],
    "Weight Gain": [
        {"name": "Chicken Biryani", "desc": "Chicken biryani with raita, mixed salad & papadum", "protein": 42, "carbs": 95, "fat": 18, "cal_factor": 0.35},
        {"name": "Beef Burger & Fries", "desc": "Homemade beef patty, whole wheat bun, sweet potato fries & side salad", "protein": 45, "carbs": 85, "fat": 28, "cal_factor": 0.35},
        {"name": "Pasta Bolognese", "desc": "Whole wheat pasta, rich beef bolognese, parmesan & garlic bread", "protein": 44, "carbs": 100, "fat": 24, "cal_factor": 0.35},
    ],
    "Improve Health / Lifestyle": [
        {"name": "Grilled Chicken & Salad", "desc": "Herb-marinated chicken, large mixed salad, olive oil dressing & whole grain roll", "protein": 34, "carbs": 30, "fat": 14, "cal_factor": 0.30},
        {"name": "Fish & Vegetables", "desc": "Pan-seared fish, roasted root vegetables, lemon & herbs", "protein": 30, "carbs": 35, "fat": 10, "cal_factor": 0.30},
        {"name": "Lentil & Spinach Curry", "desc": "Green lentil curry, wilted spinach, brown rice & yogurt", "protein": 22, "carbs": 58, "fat": 6, "cal_factor": 0.30},
    ]
}

SNACK_DB = {
    "Weight Loss": [
        {"name": "Apple & Almonds", "desc": "1 medium apple + 15 raw almonds", "cal_factor": 0.08},
        {"name": "Celery & Hummus", "desc": "Celery sticks with 3 tbsp hummus", "cal_factor": 0.08},
        {"name": "Protein Shake", "desc": "1 scoop whey protein in water/almond milk", "cal_factor": 0.08},
        {"name": "Boiled Eggs", "desc": "2 hard-boiled eggs with sea salt & pepper", "cal_factor": 0.08},
    ],
    "Muscle Building": [
        {"name": "Protein Shake & Banana", "desc": "1.5 scoop whey protein + banana for carbs", "cal_factor": 0.10},
        {"name": "Rice Cakes & Peanut Butter", "desc": "3 rice cakes with 2 tbsp peanut butter", "cal_factor": 0.10},
        {"name": "Greek Yogurt & Berries", "desc": "200g full-fat Greek yogurt with mixed berries", "cal_factor": 0.10},
        {"name": "Cheese & Crackers", "desc": "Low-fat cheese with whole grain crackers & cucumber", "cal_factor": 0.10},
    ],
    "General Fitness": [
        {"name": "Mixed Nuts & Fruit", "desc": "Handful of mixed nuts with a piece of seasonal fruit", "cal_factor": 0.09},
        {"name": "Yogurt & Honey", "desc": "Low-fat yogurt drizzled with honey & cinnamon", "cal_factor": 0.09},
        {"name": "Smoothie", "desc": "Banana, spinach & almond milk smoothie", "cal_factor": 0.09},
    ],
    "Weight Gain": [
        {"name": "Peanut Butter Toast", "desc": "2 slices whole grain toast with peanut butter & banana", "cal_factor": 0.12},
        {"name": "Mass Shake", "desc": "Mass gainer shake with whole milk, banana & oats", "cal_factor": 0.12},
        {"name": "Trail Mix", "desc": "Mixed nuts, dried fruits, seeds & dark chocolate chips", "cal_factor": 0.12},
    ],
    "Improve Health / Lifestyle": [
        {"name": "Fruit & Seeds", "desc": "Seasonal fruit salad with pumpkin & sunflower seeds", "cal_factor": 0.09},
        {"name": "Herbal Tea & Nuts", "desc": "Chamomile/green tea with a small handful of walnuts", "cal_factor": 0.09},
        {"name": "Veggie Sticks & Dip", "desc": "Carrot, cucumber & celery with tzatziki dip", "cal_factor": 0.09},
    ]
}

# ─── WORKOUT PLAN DATABASE ─────────────────────────────────────────────────────

WORKOUT_PLANS = {
    "Strength & Power": {
        "description": "Heavy compound lifts 4x per week. Focus on progressive overload for muscle and strength gains.",
        "days": [
            {"day": "Monday", "focus": "Chest & Triceps 💪", "exercises": [
                {"name": "Bench Press", "sets": "4", "reps": "8-10", "rest": "90s"},
                {"name": "Incline Dumbbell Press", "sets": "3", "reps": "10-12", "rest": "75s"},
                {"name": "Cable Crossover", "sets": "3", "reps": "12-15", "rest": "60s"},
                {"name": "Overhead Tricep Extension", "sets": "3", "reps": "12", "rest": "60s"},
                {"name": "Tricep Dips", "sets": "3", "reps": "10-12", "rest": "60s"},
            ]},
            {"day": "Tuesday", "focus": "Back & Biceps 🏋️", "exercises": [
                {"name": "Deadlift", "sets": "4", "reps": "6-8", "rest": "2min"},
                {"name": "Pull-Ups / Lat Pulldown", "sets": "4", "reps": "8-10", "rest": "90s"},
                {"name": "Bent-Over Barbell Row", "sets": "3", "reps": "10-12", "rest": "75s"},
                {"name": "Seated Cable Row", "sets": "3", "reps": "12", "rest": "60s"},
                {"name": "Barbell Bicep Curl", "sets": "3", "reps": "12", "rest": "60s"},
            ]},
            {"day": "Wednesday", "focus": "Active Recovery 🧘", "exercises": [
                {"name": "Light Walking / Cycling", "sets": "1", "reps": "30 min", "rest": "-"},
                {"name": "Full Body Stretching", "sets": "1", "reps": "20 min", "rest": "-"},
                {"name": "Foam Rolling", "sets": "1", "reps": "10 min", "rest": "-"},
            ]},
            {"day": "Thursday", "focus": "Legs & Glutes 🦵", "exercises": [
                {"name": "Back Squat", "sets": "4", "reps": "8-10", "rest": "2min"},
                {"name": "Romanian Deadlift", "sets": "3", "reps": "10-12", "rest": "90s"},
                {"name": "Leg Press", "sets": "3", "reps": "12-15", "rest": "75s"},
                {"name": "Walking Lunges", "sets": "3", "reps": "12 each", "rest": "60s"},
                {"name": "Calf Raises", "sets": "4", "reps": "20", "rest": "45s"},
            ]},
            {"day": "Friday", "focus": "Shoulders & Core 🎯", "exercises": [
                {"name": "Overhead Press", "sets": "4", "reps": "8-10", "rest": "90s"},
                {"name": "Lateral Raises", "sets": "3", "reps": "15", "rest": "60s"},
                {"name": "Face Pulls", "sets": "3", "reps": "15", "rest": "60s"},
                {"name": "Plank", "sets": "3", "reps": "60s", "rest": "45s"},
                {"name": "Cable Crunches", "sets": "3", "reps": "15", "rest": "45s"},
            ]},
            {"day": "Saturday", "focus": "Full Body 🔥", "exercises": [
                {"name": "Power Cleans", "sets": "3", "reps": "5", "rest": "2min"},
                {"name": "Push-Ups", "sets": "3", "reps": "Max", "rest": "60s"},
                {"name": "Pull-Ups", "sets": "3", "reps": "Max", "rest": "60s"},
                {"name": "Goblet Squat", "sets": "3", "reps": "15", "rest": "60s"},
                {"name": "Core Circuit", "sets": "2", "reps": "15 min", "rest": "-"},
            ]},
            {"day": "Sunday", "focus": "Rest Day 😴", "exercises": [
                {"name": "Complete Rest", "sets": "-", "reps": "-", "rest": "-"},
                {"name": "Light Walking (Optional)", "sets": "1", "reps": "20-30 min", "rest": "-"},
            ]},
        ]
    },
    "Cardio & Endurance": {
        "description": "Cardio-focused training 5x per week. Builds stamina, burns fat and improves cardiovascular health.",
        "days": [
            {"day": "Monday", "focus": "Steady State Run 🏃", "exercises": [
                {"name": "Warm-up Walk", "sets": "1", "reps": "5 min", "rest": "-"},
                {"name": "Moderate Jog/Run", "sets": "1", "reps": "30-40 min", "rest": "-"},
                {"name": "Cool-down Walk", "sets": "1", "reps": "5 min", "rest": "-"},
                {"name": "Calf & Quad Stretch", "sets": "1", "reps": "10 min", "rest": "-"},
            ]},
            {"day": "Tuesday", "focus": "Cycling / Swim 🚴", "exercises": [
                {"name": "Stationary Bike / Outdoor Cycle", "sets": "1", "reps": "45 min", "rest": "-"},
                {"name": "Swimming (Optional)", "sets": "1", "reps": "30 min", "rest": "-"},
            ]},
            {"day": "Wednesday", "focus": "HIIT Sprint 💨", "exercises": [
                {"name": "Warm-up Jog", "sets": "1", "reps": "5 min", "rest": "-"},
                {"name": "Sprint Intervals (30s sprint / 90s walk)", "sets": "8", "reps": "30s", "rest": "90s"},
                {"name": "Cool-down Walk", "sets": "1", "reps": "10 min", "rest": "-"},
            ]},
            {"day": "Thursday", "focus": "Active Recovery 🧘", "exercises": [
                {"name": "Light Yoga or Stretching", "sets": "1", "reps": "30 min", "rest": "-"},
                {"name": "Foam Rolling", "sets": "1", "reps": "10 min", "rest": "-"},
            ]},
            {"day": "Friday", "focus": "Long Run 🏅", "exercises": [
                {"name": "Warm-up Walk", "sets": "1", "reps": "5 min", "rest": "-"},
                {"name": "Long Slow Distance Run", "sets": "1", "reps": "50-60 min", "rest": "-"},
                {"name": "Full Body Stretch", "sets": "1", "reps": "15 min", "rest": "-"},
            ]},
            {"day": "Saturday", "focus": "Cross Training ⚡", "exercises": [
                {"name": "Jump Rope", "sets": "5", "reps": "3 min", "rest": "60s"},
                {"name": "Burpees", "sets": "3", "reps": "15", "rest": "60s"},
                {"name": "Mountain Climbers", "sets": "3", "reps": "30s", "rest": "30s"},
                {"name": "Box Jumps", "sets": "3", "reps": "12", "rest": "60s"},
            ]},
            {"day": "Sunday", "focus": "Rest Day 😴", "exercises": [
                {"name": "Complete Rest", "sets": "-", "reps": "-", "rest": "-"},
            ]},
        ]
    },
    "Balanced Training": {
        "description": "A balanced mix of strength and cardio 4x per week. Ideal for overall fitness and body composition.",
        "days": [
            {"day": "Monday", "focus": "Upper Body Strength 💪", "exercises": [
                {"name": "Push-Ups / Bench Press", "sets": "3", "reps": "10-15", "rest": "60s"},
                {"name": "Dumbbell Rows", "sets": "3", "reps": "12", "rest": "60s"},
                {"name": "Shoulder Press", "sets": "3", "reps": "12", "rest": "60s"},
                {"name": "Bicep Curls", "sets": "2", "reps": "15", "rest": "45s"},
                {"name": "Tricep Pushdown", "sets": "2", "reps": "15", "rest": "45s"},
            ]},
            {"day": "Tuesday", "focus": "Cardio & Core 🏃", "exercises": [
                {"name": "Moderate Jog / Brisk Walk", "sets": "1", "reps": "25 min", "rest": "-"},
                {"name": "Plank", "sets": "3", "reps": "45s", "rest": "30s"},
                {"name": "Bicycle Crunches", "sets": "3", "reps": "20", "rest": "30s"},
                {"name": "Leg Raises", "sets": "3", "reps": "15", "rest": "30s"},
            ]},
            {"day": "Wednesday", "focus": "Rest / Stretch 🧘", "exercises": [
                {"name": "Full Body Yoga / Stretching", "sets": "1", "reps": "30 min", "rest": "-"},
            ]},
            {"day": "Thursday", "focus": "Lower Body Strength 🦵", "exercises": [
                {"name": "Squats", "sets": "4", "reps": "12-15", "rest": "75s"},
                {"name": "Lunges", "sets": "3", "reps": "12 each", "rest": "60s"},
                {"name": "Glute Bridges", "sets": "3", "reps": "15", "rest": "45s"},
                {"name": "Leg Curl", "sets": "3", "reps": "12", "rest": "60s"},
                {"name": "Calf Raises", "sets": "3", "reps": "20", "rest": "30s"},
            ]},
            {"day": "Friday", "focus": "HIIT & Cardio 🔥", "exercises": [
                {"name": "Jumping Jacks", "sets": "3", "reps": "45s", "rest": "15s"},
                {"name": "High Knees", "sets": "3", "reps": "45s", "rest": "15s"},
                {"name": "Burpees", "sets": "3", "reps": "12", "rest": "45s"},
                {"name": "Mountain Climbers", "sets": "3", "reps": "30s", "rest": "30s"},
                {"name": "Jump Rope", "sets": "3", "reps": "2 min", "rest": "60s"},
            ]},
            {"day": "Saturday", "focus": "Active Fun 🏊", "exercises": [
                {"name": "Swimming / Cycling / Sport", "sets": "1", "reps": "45-60 min", "rest": "-"},
            ]},
            {"day": "Sunday", "focus": "Rest Day 😴", "exercises": [
                {"name": "Complete Rest", "sets": "-", "reps": "-", "rest": "-"},
                {"name": "Light Walk (Optional)", "sets": "1", "reps": "20 min", "rest": "-"},
            ]},
        ]
    },
    "Functional & Mobility": {
        "description": "Mobility, flexibility and functional movement patterns 4x per week. Great for overall health and injury prevention.",
        "days": [
            {"day": "Monday", "focus": "Mobility Flow 🧘", "exercises": [
                {"name": "Cat-Cow Stretches", "sets": "3", "reps": "10", "rest": "30s"},
                {"name": "Hip Circles", "sets": "2", "reps": "10 each", "rest": "30s"},
                {"name": "Shoulder Rolls & Pass-Throughs", "sets": "2", "reps": "10", "rest": "30s"},
                {"name": "Functional Squat Hold", "sets": "3", "reps": "45s", "rest": "30s"},
                {"name": "World's Greatest Stretch", "sets": "3", "reps": "5 each", "rest": "30s"},
            ]},
            {"day": "Tuesday", "focus": "Pilates Core 🎯", "exercises": [
                {"name": "Dead Bug", "sets": "3", "reps": "10", "rest": "30s"},
                {"name": "Bird Dog", "sets": "3", "reps": "10 each", "rest": "30s"},
                {"name": "Side Plank", "sets": "3", "reps": "30s each", "rest": "30s"},
                {"name": "Hollow Body Hold", "sets": "3", "reps": "20s", "rest": "40s"},
                {"name": "Glute Bridge March", "sets": "3", "reps": "12", "rest": "30s"},
            ]},
            {"day": "Wednesday", "focus": "Gentle Walk 🚶", "exercises": [
                {"name": "Brisk Walking", "sets": "1", "reps": "30-40 min", "rest": "-"},
                {"name": "Standing Stretch Routine", "sets": "1", "reps": "10 min", "rest": "-"},
            ]},
            {"day": "Thursday", "focus": "Yoga Flow 🌊", "exercises": [
                {"name": "Sun Salutations", "sets": "3", "reps": "5 rounds", "rest": "30s"},
                {"name": "Warrior Sequence", "sets": "2", "reps": "5 min", "rest": "-"},
                {"name": "Pigeon Pose", "sets": "2", "reps": "60s each", "rest": "-"},
                {"name": "Child's Pose & Savasana", "sets": "1", "reps": "10 min", "rest": "-"},
            ]},
            {"day": "Friday", "focus": "Functional Strength 💪", "exercises": [
                {"name": "Bodyweight Squats", "sets": "3", "reps": "15", "rest": "45s"},
                {"name": "Resistance Band Rows", "sets": "3", "reps": "15", "rest": "45s"},
                {"name": "Step-Ups", "sets": "3", "reps": "12 each", "rest": "45s"},
                {"name": "Modified Push-Ups", "sets": "3", "reps": "12", "rest": "45s"},
                {"name": "Pallof Press", "sets": "3", "reps": "12", "rest": "45s"},
            ]},
            {"day": "Saturday", "focus": "Light Activity 🌿", "exercises": [
                {"name": "Nature Walk / Light Hike", "sets": "1", "reps": "45-60 min", "rest": "-"},
            ]},
            {"day": "Sunday", "focus": "Full Rest 😴", "exercises": [
                {"name": "Rest & Recovery", "sets": "-", "reps": "-", "rest": "-"},
            ]},
        ]
    },
    "Weight Loss Circuit": {
        "description": "High-frequency, low-rest circuit training 5x per week to maximize calorie burn and fat loss.",
        "days": [
            {"day": "Monday", "focus": "Fat-Burn Circuit A 🔥", "exercises": [
                {"name": "Burpees", "sets": "4", "reps": "12", "rest": "30s"},
                {"name": "Jump Squats", "sets": "4", "reps": "15", "rest": "30s"},
                {"name": "Push-Ups", "sets": "4", "reps": "12", "rest": "30s"},
                {"name": "Mountain Climbers", "sets": "4", "reps": "30s", "rest": "30s"},
                {"name": "High Knees", "sets": "4", "reps": "30s", "rest": "30s"},
            ]},
            {"day": "Tuesday", "focus": "Cardio Endurance 🏃", "exercises": [
                {"name": "Brisk Walk / Jog", "sets": "1", "reps": "35 min", "rest": "-"},
                {"name": "Stair Climbing", "sets": "3", "reps": "5 min", "rest": "2min"},
            ]},
            {"day": "Wednesday", "focus": "Fat-Burn Circuit B 💪", "exercises": [
                {"name": "Dumbbell Lunges", "sets": "4", "reps": "12 each", "rest": "30s"},
                {"name": "Renegade Rows", "sets": "3", "reps": "10 each", "rest": "45s"},
                {"name": "Squat to Press", "sets": "4", "reps": "12", "rest": "30s"},
                {"name": "Plank to Row", "sets": "3", "reps": "10 each", "rest": "45s"},
                {"name": "Jumping Jacks", "sets": "4", "reps": "30s", "rest": "15s"},
            ]},
            {"day": "Thursday", "focus": "Active Recovery 🧘", "exercises": [
                {"name": "Light Yoga / Stretching", "sets": "1", "reps": "30 min", "rest": "-"},
                {"name": "Foam Rolling", "sets": "1", "reps": "10 min", "rest": "-"},
            ]},
            {"day": "Friday", "focus": "HIIT Blast ⚡", "exercises": [
                {"name": "Sprint Intervals", "sets": "6", "reps": "30s sprint / 90s walk", "rest": "-"},
                {"name": "Box Jumps / Step-Ups", "sets": "3", "reps": "15", "rest": "45s"},
                {"name": "Battle Ropes (or Jumping Jacks)", "sets": "4", "reps": "30s", "rest": "30s"},
            ]},
            {"day": "Saturday", "focus": "Long Walk 🚶", "exercises": [
                {"name": "Long Brisk Walk / Light Hike", "sets": "1", "reps": "45-60 min", "rest": "-"},
            ]},
            {"day": "Sunday", "focus": "Rest Day 😴", "exercises": [
                {"name": "Complete Rest", "sets": "-", "reps": "-", "rest": "-"},
            ]},
        ]
    }
}

ARCHETYPE_PLAN_MAP = {
    "Strength & Power": "Strength & Power",
    "Cardio & Endurance": "Cardio & Endurance",
    "Balanced Training": "Balanced Training",
    "Functional & Mobility": "Functional & Mobility",
    "Weight Loss Circuit": "Weight Loss Circuit",
}

# ─── HYDRATION SCHEDULE ────────────────────────────────────────────────────────

def get_hydration_schedule(water_target_liters, wake_hour=6):
    """Generates an hourly hydration schedule based on total daily target."""
    schedule = []
    remaining = water_target_liters

    slots = [
        (wake_hour,       0.35, "🌅 Wake-up — rehydrate after sleep"),
        (wake_hour + 1,   0.20, "🍳 Before breakfast"),
        (wake_hour + 3,   0.20, "☀️ Mid-morning boost"),
        (wake_hour + 5,   0.25, "🕐 Before lunch"),
        (wake_hour + 7,   0.20, "🌤️ Afternoon energy sip"),
        (wake_hour + 9,   0.20, "🏋️ Pre / Post workout"),
        (wake_hour + 11,  0.25, "🌙 Evening — wind down"),
        (wake_hour + 13,  0.15, "🌛 Pre-bed sip"),
    ]

    for hour_offset, fraction, note in slots:
        hour = hour_offset % 24
        amount = round(water_target_liters * fraction, 2)
        am_pm = "AM" if hour < 12 else "PM"
        display_hour = hour if hour <= 12 else hour - 12
        display_hour = 12 if display_hour == 0 else display_hour
        schedule.append({
            "time": f"{display_hour}:00 {am_pm}",
            "amount": amount,
            "note": note
        })

    return schedule


# ─── DAILY ROUTINE SCHEDULE ────────────────────────────────────────────────────

def get_daily_routine(goal, activity_level, sleep_target):
    """Returns a structured hour-by-hour daily routine."""
    is_active = "Active" in activity_level or "Moderately" in activity_level

    routine = [
        {"time": "6:00 AM",  "activity": "🌅 Wake Up & Hydrate",           "detail": "Drink 350ml water immediately. Do 5 minutes of light stretching."},
        {"time": "6:15 AM",  "activity": "🧘 Morning Mindfulness",          "detail": "5-10 min meditation or deep breathing to set a positive tone for the day."},
        {"time": "6:30 AM",  "activity": "🏋️ Workout Session",              "detail": f"Complete your daily workout as per your {'strength' if 'Muscle' in goal else 'fitness'} plan. Duration: 45-60 min."},
        {"time": "7:30 AM",  "activity": "🚿 Shower & Personal Care",       "detail": "Post-workout hygiene routine. Cold/cool shower for recovery."},
        {"time": "8:00 AM",  "activity": "🍳 Breakfast",                    "detail": "Eat your AI-planned breakfast within 60 minutes of waking up for best metabolism."},
        {"time": "9:00 AM",  "activity": "💼 Work / Study",                 "detail": "Peak focus hours. Handle your most important tasks now."},
        {"time": "10:30 AM", "activity": "💧 Hydration Check",              "detail": "Drink 200ml of water. Take a short 2-3 min standing break."},
        {"time": "1:00 PM",  "activity": "🥗 Lunch",                        "detail": "Eat your planned lunch. Avoid screens while eating to improve digestion."},
        {"time": "1:45 PM",  "activity": "🚶 Post-lunch Walk",              "detail": "10-15 minute gentle walk to aid digestion and reduce blood sugar spikes."},
        {"time": "3:00 PM",  "activity": "🍎 Afternoon Snack",              "detail": "Eat your planned healthy snack to maintain energy levels through the afternoon."},
        {"time": "3:30 PM",  "activity": "💼 Work / Study Block 2",         "detail": "Second productivity window. Tackle remaining tasks."},
        {"time": "5:30 PM",  "activity": "🏃 Evening Activity" if is_active else "🧘 Evening Stretch", "detail": "30-min evening walk, jog or yoga as a secondary activity boost." if is_active else "Light stretching and relaxation for 20-30 minutes."},
        {"time": "7:00 PM",  "activity": "🍽️ Dinner",                       "detail": "Eat your planned dinner. Keep it lighter than lunch for better sleep quality."},
        {"time": "8:00 PM",  "activity": "📖 Wind Down",                    "detail": "Read, journal, or enjoy a relaxing hobby. Avoid heavy screens after this time."},
        {"time": "9:00 PM",  "activity": "💧 Final Hydration",              "detail": "Sip 150ml of water. Herbal tea (chamomile, peppermint) aids relaxation."},
        {"time": "9:30 PM",  "activity": "🌙 Sleep Prep",                   "detail": "Dim lights, cool your room to 18-20°C. Avoid phones in bed."},
        {"time": "10:00 PM", "activity": "😴 Sleep",                        "detail": f"Target {sleep_target} hours of sleep for optimal recovery. Wake around 6:00 AM."},
    ]

    return routine


# ─── MAIN PLAN GENERATOR ───────────────────────────────────────────────────────

def generate_full_plan(profile):
    """
    Generates the complete personalized wellness plan for a user.
    Returns a dict with keys: diet_plan, workout_plan, hydration_schedule, daily_routine
    """
    goal = profile.get("goal", "General Fitness")
    archetype = profile.get("workout_archetype", "Balanced Training")
    activity_level = profile.get("activity_level", "Lightly Active (1-3 days/week)")
    calorie_target = profile.get("calorie_target", 2000)
    weight = profile.get("weight", 70)
    sleep_target = 8.0

    # Normalize goal key for DB lookup
    goal_key = goal if goal in BREAKFAST_DB else "General Fitness"

    # Pick meal options (rotate daily)
    breakfast_options = BREAKFAST_DB.get(goal_key, BREAKFAST_DB["General Fitness"])
    lunch_options = LUNCH_DB.get(goal_key, LUNCH_DB["General Fitness"])
    dinner_options = DINNER_DB.get(goal_key, DINNER_DB["General Fitness"])
    snack_options = SNACK_DB.get(goal_key, SNACK_DB["General Fitness"])

    # Build 7-day diet plan
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    diet_plan = []
    for i, day in enumerate(days):
        b = breakfast_options[i % len(breakfast_options)]
        l = lunch_options[i % len(lunch_options)]
        d = dinner_options[i % len(dinner_options)]
        s = snack_options[i % len(snack_options)]

        b_cal = round(calorie_target * b["cal_factor"])
        l_cal = round(calorie_target * l["cal_factor"])
        d_cal = round(calorie_target * d["cal_factor"])
        s_cal = round(calorie_target * s["cal_factor"])
        total = b_cal + l_cal + d_cal + s_cal

        diet_plan.append({
            "day": day,
            "breakfast": b, "breakfast_cal": b_cal,
            "lunch": l, "lunch_cal": l_cal,
            "dinner": d, "dinner_cal": d_cal,
            "snack": s, "snack_cal": s_cal,
            "total_cal": total
        })

    # Resolve workout plan
    plan_key = ARCHETYPE_PLAN_MAP.get(archetype, "Balanced Training")
    if plan_key not in WORKOUT_PLANS:
        plan_key = "Balanced Training"
    workout_plan = WORKOUT_PLANS[plan_key]

    # Hydration
    water_target = round(weight * 0.033, 1)
    hydration_schedule = get_hydration_schedule(water_target)

    # Daily routine
    daily_routine = get_daily_routine(goal, activity_level, sleep_target)

    return {
        "diet_plan": diet_plan,
        "workout_plan": workout_plan,
        "hydration_schedule": hydration_schedule,
        "daily_routine": daily_routine,
        "water_target": water_target,
        "calorie_target": round(calorie_target),
        "goal": goal,
        "archetype": archetype,
    }
