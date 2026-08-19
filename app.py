import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
import os

# Import local modules
import database as db
from ml_engine import ml_engine, GOAL_MAP, ACTIVITY_MAP
import recommendation as rec_engine
import ui_components as ui
import plan_generator as planner

# Page Config
st.set_page_config(
    page_title="AuraWellness - AI Fitness & Wellness",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Load CSS custom style
CSS_PATH = os.path.join(os.path.dirname(__file__), "assets", "styles.css")
ui.load_css(CSS_PATH)

# Ensure Database and ML Engine are prepped
if "ml_trained" not in st.session_state:
    with st.spinner("Initializing AI Models..."):
        ml_engine.train()
    st.session_state.ml_trained = True

# Helper: BMI Calculator
def calculate_bmi(weight_kg, height_cm):
    height_m = height_cm / 100.0
    bmi = weight_kg / (height_m ** 2)
    
    if bmi < 18.5:
        category = "Underweight"
    elif 18.5 <= bmi < 25.0:
        category = "Normal"
    elif 25.0 <= bmi < 30.0:
        category = "Overweight"
    else:
        category = "Obese"
        
    return round(bmi, 1), category

# Helper: Generate historical logs so that charts look stunning immediately
def prepopulate_mock_history(profile):
    """Fills SQLite daily_logs with 7 days of realistic mock data for immediate chart display."""
    today = datetime.today()
    weight = profile["weight"]
    activity = profile["activity_level"]
    archetype = profile["workout_archetype"]
    
    water_tgt = rec_engine.get_hydration_target(weight)
    steps_tgt = rec_engine.get_steps_target(activity)
    sleep_tgt = rec_engine.get_sleep_target()
    exercise_tgt = rec_engine.get_exercise_target(archetype)
    
    meals_pool = {
        "breakfast": ["Oatmeal with berries and chia seeds", "Avocado toast with poached eggs", "Greek yogurt with honey and almonds", "Protein smoothie bowl"],
        "lunch": ["Grilled chicken quinoa salad", "Turkey wrap with hummus", "Lentil soup with whole wheat bread", "Tofu stir-fry with brown rice"],
        "dinner": ["Baked salmon with asparagus", "Beef tenderloin with sweet potato", "Roasted chickpea bowl", "Pan-seared cod with spinach"],
        "snacks": ["Apple slices with peanut butter", "Mixed nuts", "Protein shake", "Rice cakes with cottage cheese"]
    }
    
    exercise_types = ["Strength Training", "Running", "Yoga", "HIIT Cardo", "Pilates", "Walking"]
    
    np.random.seed(42)
    for i in range(7, 0, -1):
        log_date = (today - timedelta(days=i)).strftime("%Y-%m-%d")
        
        # Add random variances
        w_factor = np.random.uniform(0.7, 1.25)
        st_factor = np.random.uniform(0.65, 1.3)
        sl_factor = np.random.uniform(0.8, 1.15)
        ex_factor = np.random.uniform(0.5, 1.4)
        
        # Assemble log
        log_data = {
            "water_intake": round(water_tgt * w_factor, 1),
            "steps": int(steps_tgt * st_factor),
            "distance": round((steps_tgt * st_factor * 0.00075), 2), # ~0.75m per step in km
            "exercise_type": np.random.choice(exercise_types),
            "exercise_duration": int(exercise_tgt * ex_factor),
            "exercise_sessions": 1 if ex_factor > 0.6 else 0,
            "breakfast": np.random.choice(meals_pool["breakfast"]),
            "lunch": np.random.choice(meals_pool["lunch"]),
            "dinner": np.random.choice(meals_pool["dinner"]),
            "snacks": np.random.choice(meals_pool["snacks"]),
            "sleep_duration": round(sleep_tgt * sl_factor, 1),
            "calories_consumed": round(profile["calorie_target"] * np.random.uniform(0.85, 1.15)),
            "daily_activity": "Routine tasks and standard workouts."
        }
        db.save_daily_log(log_date, log_data)

# Fetch user profile from DB to initialize session state
profile = db.get_profile()
if "user_profile" not in st.session_state:
    st.session_state.user_profile = profile

if "current_page" not in st.session_state:
    if st.session_state.user_profile:
        st.session_state.current_page = "Dashboard"
    else:
        st.session_state.current_page = "Landing"

if "selected_date" not in st.session_state:
    st.session_state.selected_date = datetime.today().strftime("%Y-%m-%d")

# Page Navigation Helper
def set_page(page_name):
    st.session_state.current_page = page_name
    st.rerun()

# ----------------- UI HEADER -----------------
st.markdown("""
<div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 20px; border-bottom: 1px solid rgba(255,255,255,0.05); padding-bottom: 15px;">
    <div style="display: flex; align-items: center; gap: 10px;">
        <span style="font-size: 2.2rem;">⚡</span>
        <span style="font-size: 1.8rem; font-weight: 800; letter-spacing: 2px; background: linear-gradient(135deg, #00f2fe 0%, #4facfe 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">AURAWELLNESS</span>
    </div>
    <div style="font-size: 0.85rem; color: #5d616f; font-weight: 500; text-transform: uppercase; letter-spacing: 1px;">AI Fitness & Health Platform</div>
</div>
""", unsafe_allow_html=True)

# ----------------- NAVIGATION PILLS -----------------
# Render top navigation bar only if user is logged in (i.e. profile exists) and not on landing page
if st.session_state.user_profile and st.session_state.current_page != "Landing":
    cols = st.columns([1, 1, 1.2, 1.2, 1, 1, 1])

    with cols[0]:
        if st.button("📊 Dashboard", use_container_width=True, type="secondary" if st.session_state.current_page != "Dashboard" else "primary"):
            set_page("Dashboard")
    with cols[1]:
        if st.button("📋 My Plan", use_container_width=True, type="secondary" if st.session_state.current_page != "My Plan" else "primary"):
            set_page("My Plan")
    with cols[2]:
        if st.button("✏️ Daily Tracking", use_container_width=True, type="secondary" if st.session_state.current_page != "Daily Tracking" else "primary"):
            set_page("Daily Tracking")
    with cols[3]:
        if st.button("🤖 AI Recommendations", use_container_width=True, type="secondary" if st.session_state.current_page != "AI Recommendations" else "primary"):
            set_page("AI Recommendations")
    with cols[4]:
        if st.button("📈 Analytics", use_container_width=True, type="secondary" if st.session_state.current_page != "Progress Analytics" else "primary"):
            set_page("Progress Analytics")
    with cols[5]:
        if st.button("🔍 Assessment", use_container_width=True, type="secondary" if st.session_state.current_page != "Fitness Assessment" else "primary"):
            set_page("Fitness Assessment")
    with cols[6]:
        if st.button("👤 Profile", use_container_width=True, type="secondary" if st.session_state.current_page != "User Profile" else "primary"):
            set_page("User Profile")
    st.markdown("---")

# ==============================================================================
# 1. LANDING PAGE
# ==============================================================================
if st.session_state.current_page == "Landing":
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    ui.render_hero(
        "BUILD YOUR",
        "STRONGER SELF.",
        "AuraWellness is a premium, AI-driven personal health assistant. By combining advanced machine learning prediction engines with custom biometric assessments, it crafts personalized hydration, sleep, exercise, and nutritional plans to accelerate your wellness journey."
    )
    
    col_c, col_btn, col_r = st.columns([2, 1.5, 2])
    with col_btn:
        if st.button("START YOUR FITNESS JOURNEY", use_container_width=True, type="primary"):
            if st.session_state.user_profile:
                set_page("Dashboard")
            else:
                set_page("User Profile")
                
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    # Feature Showcase Grid
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""
        <div class="premium-card" style="text-align: center; height: 100%;">
            <div style="font-size: 2.5rem; margin-bottom: 10px;">🧠</div>
            <h3>Scikit-Learn ML Insights</h3>
            <p style="color: #8a8f9d; font-size: 0.9rem;">Predicts targeted caloric needs, macronutrient splits, and custom training archetypes matched directly to your physiological metrics.</p>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div class="premium-card" style="text-align: center; height: 100%;">
            <div style="font-size: 2.5rem; margin-bottom: 10px;">📅</div>
            <h3>Intelligent Habit Logs</h3>
            <p style="color: #8a8f9d; font-size: 0.9rem;">Seamless daily tracking for hydration metrics, walk step milestones, caloric intake logs, sleeping patterns, and workout active times.</p>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown("""
        <div class="premium-card" style="text-align: center; height: 100%;">
            <div style="font-size: 2.5rem; margin-bottom: 10px;">📊</div>
            <h3>Dynamic Visual Trends</h3>
            <p style="color: #8a8f9d; font-size: 0.9rem;">Deep progress monitoring using beautiful interactive charts showing water volumes, sleep averages, and steps analytics over time.</p>
        </div>
        """, unsafe_allow_html=True)

# ==============================================================================
# 2. USER PROFILE / SETUP
# ==============================================================================
elif st.session_state.current_page == "User Profile":
    st.markdown("<h2 style='text-align: center; margin-bottom: 30px;'>Configure Your Profile</h2>", unsafe_allow_html=True)
    
    profile_exists = st.session_state.user_profile is not None
    current_prof = st.session_state.user_profile or {}
    
    with st.form("profile_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.text_input("Full Name", value=current_prof.get("name", ""))
            age = st.number_input("Age (years)", min_value=12, max_value=120, value=current_prof.get("age", 25))
            gender = st.selectbox("Gender", ["Male", "Female"], index=0 if current_prof.get("gender") != "Female" else 1)
            height = st.number_input("Height (cm)", min_value=100.0, max_value=250.0, value=current_prof.get("height", 175.0))
            weight = st.number_input("Weight (kg)", min_value=30.0, max_value=300.0, value=current_prof.get("weight", 70.0))
            
        with col2:
            goal = st.selectbox("Primary Fitness Goal", 
                                ["Weight Loss", "Weight Gain", "Muscle Building", "General Fitness", "Improve Health / Lifestyle"],
                                index=GOAL_MAP.get(current_prof.get("goal", ""), 3))
            
            activity = st.selectbox("Daily Activity Level", 
                                    ["Sedentary (Little to no exercise)", 
                                     "Lightly Active (1-3 days/week)", 
                                     "Moderately Active (3-5 days/week)", 
                                     "Very Active (6-7 days/week)"],
                                    index=ACTIVITY_MAP.get(current_prof.get("activity_level", ""), 2))
            
            routine = st.text_area("Daily Routine & Lifestyle Description", 
                                   value=current_prof.get("routine", ""),
                                   placeholder="Describe your general work style, sleep routine, and dietary habits...")
        
        st.markdown("<br>", unsafe_allow_html=True)
        btn_col_l, btn_col_c, btn_col_r = st.columns([1.5, 1, 1.5])
        with btn_col_c:
            submit_profile = st.form_submit_button("Save & Generate Assessment", use_container_width=True)
            
        if submit_profile:
            if not name.strip():
                st.error("Please enter a valid name.")
            else:
                with st.spinner("Analyzing profile using Scikit-Learn models..."):
                    # Calculate BMI
                    bmi, bmi_cat = calculate_bmi(weight, height)
                    
                    # Run predictions using ML engine
                    ml_targets = ml_engine.predict_wellness_targets(age, gender, height, weight, activity, goal)
                    
                    # Package profile data
                    profile_payload = {
                        "name": name.strip(),
                        "age": int(age),
                        "gender": gender,
                        "height": float(height),
                        "weight": float(weight),
                        "activity_level": activity,
                        "goal": goal,
                        "routine": routine.strip(),
                        "bmi": bmi,
                        "bmi_category": bmi_cat,
                        "calorie_target": ml_targets["calories"],
                        "macro_split": ml_targets["macro_split"],
                        "protein_target": ml_targets["protein_g"],
                        "carb_target": ml_targets["carb_g"],
                        "fat_target": ml_targets["fat_g"],
                        "workout_archetype": ml_targets["workout_archetype"]
                    }
                    
                    # Save to DB
                    db.save_profile(profile_payload)
                    
                    # Refresh Session State
                    st.session_state.user_profile = db.get_profile()
                    
                    # Pre-populate history if it's the first time
                    if not profile_exists:
                        prepopulate_mock_history(st.session_state.user_profile)
                        
                    st.success("Profile saved successfully!")
                    set_page("Fitness Assessment")

# ==============================================================================
# 3. FITNESS ASSESSMENT
# ==============================================================================
elif st.session_state.current_page == "Fitness Assessment":
    prof = st.session_state.user_profile
    if not prof:
        st.warning("Please configure your profile first.")
        if st.button("Go to Profile Setup"):
            set_page("User Profile")
    else:
        st.markdown(f"<h2 style='text-align: center; margin-bottom: 25px;'>Fitness & Metabolic Assessment</h2>", unsafe_allow_html=True)
        st.markdown(f"<p style='text-align: center; color: #8a8f9d; margin-top: -15px; margin-bottom: 40px;'>Analysis of biometrics for <b>{prof['name']}</b> using trained machine learning models.</p>", unsafe_allow_html=True)
        
        col1, col2 = st.columns([1, 1.2])
        
        with col1:
            # BMI Assessment Card
            st.markdown("<h3 style='margin-bottom:15px;'>Biometric Overview</h3>", unsafe_allow_html=True)
            
            # Map BMI categories to colors
            bmi_colors = {
                "Underweight": "orange",
                "Normal": "green",
                "Overweight": "orange",
                "Obese": "orange"
            }
            color_sel = bmi_colors.get(prof["bmi_category"], "blue")
            
            ui.metric_card("Calculated BMI", f"{prof['bmi']}", f"Category: {prof['bmi_category']}", color=color_sel)
            
            # General details
            st.markdown(f"""
            <div class="premium-card">
                <h3>Physique Summary</h3>
                <div style="display: flex; flex-direction: column; gap: 10px; margin-top: 15px;">
                    <div style="display: flex; justify-content: space-between;"><span style="color:#8a8f9d;">Age:</span><strong>{prof['age']} years</strong></div>
                    <div style="display: flex; justify-content: space-between;"><span style="color:#8a8f9d;">Height:</span><strong>{prof['height']} cm</strong></div>
                    <div style="display: flex; justify-content: space-between;"><span style="color:#8a8f9d;">Weight:</span><strong>{prof['weight']} kg</strong></div>
                    <div style="display: flex; justify-content: space-between;"><span style="color:#8a8f9d;">Activity Level:</span><strong>{prof['activity_level'].split(' (')[0]}</strong></div>
                    <div style="display: flex; justify-content: space-between;"><span style="color:#8a8f9d;">Primary Goal:</span><strong style="color: #4facfe;">{prof['goal']}</strong></div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
        with col2:
            st.markdown("<h3 style='margin-bottom:15px;'>AI Predicted Targets</h3>", unsafe_allow_html=True)

            # Pre-extract values to avoid f-string quote conflicts
            cal_target = round(prof['calorie_target'])
            macro_split = prof.get('macro_split', 'Balanced')
            protein_g = prof.get('protein_target', 0)
            carb_g = prof.get('carb_target', 0)
            fat_g = prof.get('fat_target', 0)
            archetype = prof.get('workout_archetype', 'General Fitness')
            goal_label = prof.get('goal', '')

            # Calorie + Macro Split header card
            st.markdown(
                f'<div class="premium-card">'
                f'<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:20px;">'
                f'<div><div class="metric-label">Estimated Daily Target</div>'
                f'<div class="metric-value">{cal_target} <span style="font-size:1rem;color:#8a8f9d;font-weight:400;">kcal/day</span></div></div>'
                f'<div style="background:rgba(0,242,254,0.07);padding:8px 16px;border-radius:8px;border:1px solid rgba(0,242,254,0.15);text-align:center;">'
                f'<span style="font-size:0.75rem;text-transform:uppercase;color:#8a8f9d;">Macro Split</span><br>'
                f'<strong style="color:#00f2fe;font-size:0.95rem;">{macro_split}</strong></div></div>'
                f'<h4 style="margin-top:20px;font-weight:500;font-size:0.95rem;color:#f1f3f9;">Target Macronutrient Allocation</h4>'
                f'<div style="display:flex;gap:15px;margin-top:10px;">'
                f'<div style="flex:1;text-align:center;background:rgba(255,255,255,0.02);padding:12px;border-radius:8px;">'
                f'<span style="font-size:0.75rem;color:#8a8f9d;text-transform:uppercase;">Protein</span><br>'
                f'<strong style="color:#ffb199;font-size:1.25rem;">{protein_g}g</strong></div>'
                f'<div style="flex:1;text-align:center;background:rgba(255,255,255,0.02);padding:12px;border-radius:8px;">'
                f'<span style="font-size:0.75rem;color:#8a8f9d;text-transform:uppercase;">Carbs</span><br>'
                f'<strong style="color:#00f2fe;font-size:1.25rem;">{carb_g}g</strong></div>'
                f'<div style="flex:1;text-align:center;background:rgba(255,255,255,0.02);padding:12px;border-radius:8px;">'
                f'<span style="font-size:0.75rem;color:#8a8f9d;text-transform:uppercase;">Fats</span><br>'
                f'<strong style="color:#96c93d;font-size:1.25rem;">{fat_g}g</strong></div>'
                f'</div></div>',
                unsafe_allow_html=True
            )

            # Workout Archetype Card
            st.markdown(
                f'<div class="premium-card">'
                f'<div class="metric-label">Predicted Workout Archetype</div>'
                f'<h3 style="color:#00b09b;margin-top:5px;font-weight:700;">{archetype}</h3>'
                f'<p style="color:#8a8f9d;font-size:0.9rem;margin-top:10px;line-height:1.5;">'
                f'The Decision Tree classifier categorized your training archetype based on your fitness goals and daily activity levels. '
                f'This layout prioritizes energy pathways suited for your <b>{goal_label}</b> roadmap.</p>'
                f'</div>',
                unsafe_allow_html=True
            )
            
        st.markdown("<br>", unsafe_allow_html=True)
        col_bl, col_bc, col_br = st.columns([2, 1.5, 2])
        with col_bc:
            if st.button("PROCEED TO DASHBOARD", use_container_width=True, type="primary"):
                set_page("Dashboard")

# ==============================================================================
# 4. DASHBOARD
# ==============================================================================
elif st.session_state.current_page == "Dashboard":
    prof = st.session_state.user_profile
    if not prof:
        st.warning("Please configure your profile first.")
        if st.button("Go to Profile Setup"):
            set_page("User Profile")
    else:
        # Load logged metrics for selected date
        selected_date = st.session_state.selected_date
        
        # Add a date navigator at the top of the dashboard
        col_nav_d1, col_nav_d2, col_nav_d3 = st.columns([2.5, 1.5, 2.5])
        with col_nav_d2:
            st.date_input("Select Dashboard Date", value=datetime.strptime(selected_date, "%Y-%m-%d"), key="dash_date_input")
            # Update state date if changed
            if st.session_state.dash_date_input.strftime("%Y-%m-%d") != selected_date:
                st.session_state.selected_date = st.session_state.dash_date_input.strftime("%Y-%m-%d")
                st.rerun()
                
        today_log = db.get_daily_log(selected_date)
        
        # Welcome message
        st.markdown(f"<h2>Welcome back, {prof['name']}! 👋</h2>", unsafe_allow_html=True)
        st.markdown(f"<p style='color: #8a8f9d; margin-top: -15px; margin-bottom: 25px;'>Here is your fitness dashboard for <b>{datetime.strptime(selected_date, '%Y-%m-%d').strftime('%A, %b %d, %Y')}</b>.</p>", unsafe_allow_html=True)
        
        # Calculate Adherence Score
        # Adherence score is calculated as average completion percentage of Water, Steps, Exercise, Sleep targets
        water_target = rec_engine.get_hydration_target(prof["weight"])
        steps_target = rec_engine.get_steps_target(prof["activity_level"])
        sleep_target = rec_engine.get_sleep_target()
        exercise_target = rec_engine.get_exercise_target(prof["workout_archetype"])
        
        w_pct = min(1.0, today_log["water_intake"] / water_target if water_target > 0 else 0)
        s_pct = min(1.0, today_log["steps"] / steps_target if steps_target > 0 else 0)
        sl_pct = min(1.0, today_log["sleep_duration"] / sleep_target if sleep_target > 0 else 0)
        ex_pct = min(1.0, today_log["exercise_duration"] / exercise_target if exercise_target > 0 else 0)
        
        adherence_score = round(((w_pct + s_pct + sl_pct + ex_pct) / 4.0) * 100)
        
        # Top Grid: Core Biometrics & Daily Compliance
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            ui.metric_card("Fitness Goal", prof["goal"], "Target Focus Path", color="blue")
        with col2:
            ui.metric_card("Body Mass Index", f"{prof['bmi']}", f"Category: {prof['bmi_category']}", color="green")
        with col3:
            ui.metric_card("Daily Target", f"{round(prof['calorie_target'])} kcal", f"Split: {prof.get('macro_split', 'Balanced')}", color="blue")
        with col4:
            # Color adherence based on score
            adh_color = "orange" if adherence_score < 50 else ("green" if adherence_score >= 80 else "blue")
            ui.metric_card("Daily Compliance", f"{adherence_score}%", "Metric Adherence Score", color=adh_color)
            
        st.markdown("<h3 style='margin: 20px 0 15px 0;'>Habit Progress & Tracking</h3>", unsafe_allow_html=True)
        
        # Progress Bars Grid
        col_p1, col_p2 = st.columns(2)
        with col_p1:
            ui.progress_bar("Hydration Progress", today_log["water_intake"], water_target, "Liters", color="blue")
            ui.progress_bar("Walking Steps", today_log["steps"], steps_target, "steps", color="green")
            
        with col_p2:
            ui.progress_bar("Exercise Duration", today_log["exercise_duration"], exercise_target, "minutes", color="orange")
            ui.progress_bar("Sleep Log", today_log["sleep_duration"], sleep_target, "hours", color="blue")
            
        # Summary details for other daily entries
        col_s1, col_s2 = st.columns([1, 1])
        with col_s1:
            st.markdown(f"""
            <div class="premium-card" style="height: 100%;">
                <h3>Diet & Food Intake</h3>
                <div style="display: flex; flex-direction: column; gap: 12px; margin-top: 15px;">
                    <div><span style="font-size: 0.75rem; text-transform: uppercase; color: #8a8f9d;">Breakfast:</span><br><strong style="font-size: 0.95rem; color:#ffffff;">{today_log['breakfast'] or 'Not Logged'}</strong></div>
                    <div><span style="font-size: 0.75rem; text-transform: uppercase; color: #8a8f9d;">Lunch:</span><br><strong style="font-size: 0.95rem; color:#ffffff;">{today_log['lunch'] or 'Not Logged'}</strong></div>
                    <div><span style="font-size: 0.75rem; text-transform: uppercase; color: #8a8f9d;">Dinner:</span><br><strong style="font-size: 0.95rem; color:#ffffff;">{today_log['dinner'] or 'Not Logged'}</strong></div>
                    <div><span style="font-size: 0.75rem; text-transform: uppercase; color: #8a8f9d;">Snacks:</span><br><strong style="font-size: 0.95rem; color:#ffffff;">{today_log['snacks'] or 'Not Logged'}</strong></div>
                    <hr style="margin: 8px 0; border: 0; border-top: 1px solid rgba(255, 255, 255, 0.05);">
                    <div style="display: flex; justify-content: space-between; align-items:center;">
                        <span style="color: #8a8f9d;">Logged Caloric Intake:</span>
                        <strong style="color: #ffb199; font-size: 1.1rem;">{round(today_log['calories_consumed'])} kcal</strong>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
        with col_s2:
            st.markdown(f"""
            <div class="premium-card" style="height: 100%;">
                <h3>Activity & Workouts</h3>
                <div style="display: flex; flex-direction: column; gap: 12px; margin-top: 15px;">
                    <div><span style="font-size: 0.75rem; text-transform: uppercase; color: #8a8f9d;">Distance Covered:</span><br><strong style="font-size: 1.15rem; color:#00b09b;">{today_log['distance']} km</strong></div>
                    <div><span style="font-size: 0.75rem; text-transform: uppercase; color: #8a8f9d;">Exercise Type:</span><br><strong style="font-size: 1.05rem; color:#ffffff;">{today_log['exercise_type'] or 'None'}</strong></div>
                    <div><span style="font-size: 0.75rem; text-transform: uppercase; color: #8a8f9d;">Exercise Sessions:</span><br><strong style="font-size: 1.05rem; color:#ffffff;">{today_log['exercise_sessions']} session(s)</strong></div>
                    <div><span style="font-size: 0.75rem; text-transform: uppercase; color: #8a8f9d;">Daily Routine / Activity Level:</span><br><strong style="font-size: 0.9rem; color:#8a8f9d; font-weight:400;">{today_log['daily_activity'] or 'No details written.'}</strong></div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
        st.markdown("<br>", unsafe_allow_html=True)
        col_bl, col_bc, col_br = st.columns([2.5, 1, 2.5])
        with col_bc:
            if st.button("✏️ Log Today's Metrics", use_container_width=True, type="primary"):
                set_page("Daily Tracking")

# ==============================================================================
# 5. DAILY TRACKING
# ==============================================================================
elif st.session_state.current_page == "Daily Tracking":
    prof = st.session_state.user_profile
    if not prof:
        st.warning("Please configure your profile first.")
        if st.button("Go to Profile Setup"):
            set_page("User Profile")
    else:
        selected_date = st.session_state.selected_date
        
        st.markdown(f"<h2 style='text-align: center; margin-bottom: 5px;'>Log Daily Habits</h2>", unsafe_allow_html=True)
        st.markdown(f"<p style='text-align: center; color: #8a8f9d; margin-bottom: 30px;'>Log wellness metrics for: <b>{datetime.strptime(selected_date, '%Y-%m-%d').strftime('%A, %b %d, %Y')}</b></p>", unsafe_allow_html=True)
        
        # Load existing values
        existing_log = db.get_daily_log(selected_date)
        
        with st.form("daily_tracking_form"):
            col_date_picker, col_filler = st.columns([1.5, 3])
            with col_date_picker:
                tracking_date = st.date_input("Date to Log", value=datetime.strptime(selected_date, "%Y-%m-%d"))
            
            st.markdown("---")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("<h3 style='color:#00f2fe;'>💧 Hydration & 👣 Activity</h3>", unsafe_allow_html=True)
                water = st.number_input("Water Consumed (Liters)", min_value=0.0, max_value=10.0, value=float(existing_log["water_intake"]), step=0.1)
                steps = st.number_input("Steps Counted", min_value=0, max_value=100000, value=int(existing_log["steps"]), step=500)
                distance = st.number_input("Distance Covered (km)", min_value=0.0, max_value=100.0, value=float(existing_log["distance"]), step=0.1)
                
                st.markdown("<h3 style='color:#ffb199; margin-top:20px;'>🏋️ Exercise & 🛌 Sleep</h3>", unsafe_allow_html=True)
                ex_type = st.text_input("Workout/Exercise Type", value=existing_log["exercise_type"] or "", placeholder="e.g. Strength Training, Run, Swim, Yoga")
                ex_duration = st.number_input("Workout Duration (minutes)", min_value=0, max_value=480, value=int(existing_log["exercise_duration"]), step=5)
                ex_sessions = st.number_input("Workout Sessions", min_value=0, max_value=10, value=int(existing_log["exercise_sessions"]), step=1)
                sleep = st.number_input("Sleep Duration (hours)", min_value=0.0, max_value=24.0, value=float(existing_log["sleep_duration"]), step=0.5)
                
            with col2:
                st.markdown("<h3 style='color:#96c93d;'>🍎 Nutrition & Meals</h3>", unsafe_allow_html=True)
                breakfast = st.text_input("Breakfast", value=existing_log["breakfast"] or "", placeholder="What did you eat for breakfast?")
                lunch = st.text_input("Lunch", value=existing_log["lunch"] or "", placeholder="What did you eat for lunch?")
                dinner = st.text_input("Dinner", value=existing_log["dinner"] or "", placeholder="What did you eat for dinner?")
                snacks = st.text_input("Snacks", value=existing_log["snacks"] or "", placeholder="Any snacks?")
                calories = st.number_input("Est. Calories Consumed (kcal)", min_value=0, max_value=10000, value=int(existing_log["calories_consumed"]), step=50)
                
                st.markdown("<h3 style='color:#8a8f9d; margin-top:20px;'>📝 Additional Daily Activity</h3>", unsafe_allow_html=True)
                activity_notes = st.text_area("Lifestyle / Daily Activity Details", value=existing_log["daily_activity"] or "", placeholder="Any additional notes about your day, active movement, or energy levels...")
                
            st.markdown("<br>", unsafe_allow_html=True)
            btn_col_l, btn_col_c, btn_col_r = st.columns([2, 1, 2])
            with btn_col_c:
                save_log = st.form_submit_button("Save Daily Log", use_container_width=True)
                
            if save_log:
                log_date_str = tracking_date.strftime("%Y-%m-%d")
                
                log_payload = {
                    "water_intake": water,
                    "steps": steps,
                    "distance": distance,
                    "exercise_type": ex_type.strip(),
                    "exercise_duration": ex_duration,
                    "exercise_sessions": ex_sessions,
                    "breakfast": breakfast.strip(),
                    "lunch": lunch.strip(),
                    "dinner": dinner.strip(),
                    "snacks": snacks.strip(),
                    "sleep_duration": sleep,
                    "calories_consumed": calories,
                    "daily_activity": activity_notes.strip()
                }
                
                db.save_daily_log(log_date_str, log_payload)
                st.session_state.selected_date = log_date_str
                st.success("Daily progress logged successfully!")
                set_page("Dashboard")

# ==============================================================================
# 6. AI RECOMMENDATIONS
# ==============================================================================
elif st.session_state.current_page == "AI Recommendations":
    prof = st.session_state.user_profile
    if not prof:
        st.warning("Please configure your profile first.")
        if st.button("Go to Profile Setup"):
            set_page("User Profile")
    else:
        selected_date = st.session_state.selected_date
        today_log = db.get_daily_log(selected_date)
        
        st.markdown(f"<h2 style='text-align: center;'>🤖 AI Wellness Advisor</h2>", unsafe_allow_html=True)
        st.markdown(f"<p style='text-align: center; color: #8a8f9d; margin-bottom: 30px;'>Personalized feedback generated by comparing targets with metrics logged for <b>{datetime.strptime(selected_date, '%Y-%m-%d').strftime('%A, %b %d, %Y')}</b>.</p>", unsafe_allow_html=True)
        
        col_targets, col_recs = st.columns([1, 1.5])
        
        with col_targets:
            st.markdown("<h3>Biometric Targets</h3>", unsafe_allow_html=True)
            
            water_target = rec_engine.get_hydration_target(prof["weight"])
            steps_target = rec_engine.get_steps_target(prof["activity_level"])
            sleep_target = rec_engine.get_sleep_target()
            exercise_target = rec_engine.get_exercise_target(prof["workout_archetype"])
            
            st.markdown(f"""
            <div class="premium-card">
                <div style="display: flex; flex-direction: column; gap: 14px;">
                    <div style="display: flex; justify-content: space-between;">
                        <span style="color:#8a8f9d;">Water Target:</span>
                        <strong>{water_target} Liters</strong>
                    </div>
                    <div style="display: flex; justify-content: space-between;">
                        <span style="color:#8a8f9d;">Steps Milestone:</span>
                        <strong>{steps_target:,} steps</strong>
                    </div>
                    <div style="display: flex; justify-content: space-between;">
                        <span style="color:#8a8f9d;">Active Minutes:</span>
                        <strong>{exercise_target} mins ({prof['workout_archetype']})</strong>
                    </div>
                    <div style="display: flex; justify-content: space-between;">
                        <span style="color:#8a8f9d;">Calories Allocation:</span>
                        <strong>{round(prof['calorie_target'])} kcal ({prof.get('macro_split', 'Balanced')})</strong>
                    </div>
                    <div style="display: flex; justify-content: space-between;">
                        <span style="color:#8a8f9d;">Sleep Goal:</span>
                        <strong>{sleep_target} hours</strong>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Tips Card
            ui.info_callout("AuraWellness analyzes your historical and daily outputs. Check recommendations at the end of each day to adjust meals and habits for the following day.")
            
        with col_recs:
            st.markdown("<h3>Personalized Recommendations</h3>", unsafe_allow_html=True)
            
            recs = rec_engine.generate_recommendations(prof, today_log)
            
            if not recs:
                st.info("Log some daily metrics under 'Daily Tracking' to generate recommendations!")
            else:
                for r in recs:
                    ui.render_recommendation(r)
                    
            st.markdown("<p style='font-size: 0.75rem; color:#5d616f; text-align: center; margin-top:20px;'>Disclaimer: AuraWellness provides lifestyle recommendations for healthy habits and tracking. Please consult a qualified practitioner for clinical or nutritional guidance.</p>", unsafe_allow_html=True)

# ==============================================================================
# 7. PROGRESS ANALYTICS
# ==============================================================================
elif st.session_state.current_page == "Progress Analytics":
    prof = st.session_state.user_profile
    if not prof:
        st.warning("Please configure your profile first.")
        if st.button("Go to Profile Setup"):
            set_page("User Profile")
    else:
        st.markdown(f"<h2 style='text-align: center;'>📈 Wellness Analytics</h2>", unsafe_allow_html=True)
        st.markdown(f"<p style='text-align: center; color: #8a8f9d; margin-bottom: 30px;'>Historical progress charts showing habit compliance and trends.</p>", unsafe_allow_html=True)
        
        # Load all history logs
        logs = db.get_all_daily_logs()
        
        if len(logs) == 0:
            st.info("Log daily habits over multiple days to populate charts!")
        else:
            df = pd.DataFrame(logs)
            # Make sure log_date is sorted
            df = df.sort_values(by="log_date")
            
            # Targets
            water_target = rec_engine.get_hydration_target(prof["weight"])
            steps_target = rec_engine.get_steps_target(prof["activity_level"])
            sleep_target = rec_engine.get_sleep_target()
            calorie_target = prof["calorie_target"]
            
            # 1st Row: Steps & Calories
            col_ch1, col_ch2 = st.columns(2)
            
            with col_ch1:
                st.markdown("<h3>Steps vs. Daily Milestone</h3>", unsafe_allow_html=True)
                fig_steps = go.Figure()
                fig_steps.add_trace(go.Bar(
                    x=df["log_date"],
                    y=df["steps"],
                    name="Logged Steps",
                    marker_color="#00b09b"
                ))
                fig_steps.add_trace(go.Scatter(
                    x=df["log_date"],
                    y=[steps_target]*len(df),
                    name="Target Line",
                    line=dict(color="#ff0844", width=2, dash="dash")
                ))
                fig_steps.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    font_color="#f1f3f9",
                    margin=dict(l=20, r=20, t=20, b=20),
                    height=300,
                    xaxis=dict(gridcolor="rgba(255,255,255,0.05)"),
                    yaxis=dict(gridcolor="rgba(255,255,255,0.05)"),
                    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
                )
                st.plotly_chart(fig_steps, use_container_width=True)
                
            with col_ch2:
                st.markdown("<h3>Daily Calories Intake vs. Target</h3>", unsafe_allow_html=True)
                fig_cals = go.Figure()
                fig_cals.add_trace(go.Scatter(
                    x=df["log_date"],
                    y=df["calories_consumed"],
                    name="Consumed (kcal)",
                    mode="lines+markers",
                    line=dict(color="#ffb199", width=3),
                    marker=dict(size=8)
                ))
                fig_cals.add_trace(go.Scatter(
                    x=df["log_date"],
                    y=[calorie_target]*len(df),
                    name="Calorie Target",
                    line=dict(color="#00f2fe", width=2, dash="dash")
                ))
                fig_cals.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    font_color="#f1f3f9",
                    margin=dict(l=20, r=20, t=20, b=20),
                    height=300,
                    xaxis=dict(gridcolor="rgba(255,255,255,0.05)"),
                    yaxis=dict(gridcolor="rgba(255,255,255,0.05)"),
                    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
                )
                st.plotly_chart(fig_cals, use_container_width=True)
                
            # 2nd Row: Hydration & Sleep
            col_ch3, col_ch4 = st.columns(2)
            
            with col_ch3:
                st.markdown("<h3>Hydration (Liters) Trend</h3>", unsafe_allow_html=True)
                fig_water = go.Figure()
                fig_water.add_trace(go.Scatter(
                    x=df["log_date"],
                    y=df["water_intake"],
                    name="Logged Water",
                    mode="lines+markers",
                    line=dict(color="#4facfe", width=3),
                    marker=dict(size=8)
                ))
                fig_water.add_trace(go.Scatter(
                    x=df["log_date"],
                    y=[water_target]*len(df),
                    name="Water Target",
                    line=dict(color="#00b09b", width=2, dash="dash")
                ))
                fig_water.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    font_color="#f1f3f9",
                    margin=dict(l=20, r=20, t=20, b=20),
                    height=300,
                    xaxis=dict(gridcolor="rgba(255,255,255,0.05)"),
                    yaxis=dict(gridcolor="rgba(255,255,255,0.05)"),
                    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
                )
                st.plotly_chart(fig_water, use_container_width=True)
                
            with col_ch4:
                st.markdown("<h3>Sleep Log (Hours) vs Target</h3>", unsafe_allow_html=True)
                fig_sleep = go.Figure()
                fig_sleep.add_trace(go.Bar(
                    x=df["log_date"],
                    y=df["sleep_duration"],
                    name="Logged Sleep",
                    marker_color="#9b5de5"
                ))
                fig_sleep.add_trace(go.Scatter(
                    x=df["log_date"],
                    y=[sleep_target]*len(df),
                    name="Target Line",
                    line=dict(color="#ff0844", width=2, dash="dash")
                ))
                fig_sleep.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    font_color="#f1f3f9",
                    margin=dict(l=20, r=20, t=20, b=20),
                    height=300,
                    xaxis=dict(gridcolor="rgba(255,255,255,0.05)"),
                    yaxis=dict(gridcolor="rgba(255,255,255,0.05)"),
                    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
                )
                st.plotly_chart(fig_sleep, use_container_width=True)

# ==============================================================================
# 8. MY PLAN — AI GENERATED PERSONAL PLAN
# ==============================================================================
elif st.session_state.current_page == "My Plan":
    prof = st.session_state.user_profile
    if not prof:
        st.warning("Please configure your profile first.")
        if st.button("Go to Profile Setup"):
            set_page("User Profile")
    else:
        name = prof.get("name", "You")
        goal = prof.get("goal", "General Fitness")
        archetype = prof.get("workout_archetype", "Balanced Training")

        st.markdown(f"<h2 style='text-align:center;'>📋 Your Personal Wellness Plan</h2>", unsafe_allow_html=True)
        st.markdown(f"<p style='text-align:center;color:#8a8f9d;margin-bottom:30px;'>Auto-generated for <b>{name}</b> based on your goal: <b style='color:#00f5d4;'>{goal}</b></p>", unsafe_allow_html=True)

        with st.spinner("🤖 Generating your personalized plan..."):
            plan = planner.generate_full_plan(prof)

        # ── PLAN SUMMARY CARDS ──────────────────────────────────────────────────
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.markdown(f'<div class="premium-card" style="text-align:center;"><div class="metric-label">Daily Calories</div><div class="metric-value">{plan["calorie_target"]}</div><div class="metric-sub">kcal / day</div></div>', unsafe_allow_html=True)
        with c2:
            st.markdown(f'<div class="premium-card" style="text-align:center;"><div class="metric-label">Water Target</div><div class="metric-value-green">{plan["water_target"]}L</div><div class="metric-sub">per day</div></div>', unsafe_allow_html=True)
        with c3:
            st.markdown(f'<div class="premium-card" style="text-align:center;"><div class="metric-label">Workout Style</div><div class="metric-value-purple" style="font-size:1.2rem;">{archetype}</div><div class="metric-sub">this week</div></div>', unsafe_allow_html=True)
        with c4:
            st.markdown(f'<div class="premium-card" style="text-align:center;"><div class="metric-label">Sleep Target</div><div class="metric-value-orange">8h</div><div class="metric-sub">per night</div></div>', unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # ── TABS ────────────────────────────────────────────────────────────────
        tab1, tab2, tab3, tab4 = st.tabs(["🍽️ 7-Day Diet Plan", "💪 Workout Schedule", "💧 Hydration Plan", "📅 Daily Routine"])

        # ── TAB 1: DIET PLAN ───────────────────────────────────────────────────
        with tab1:
            st.markdown(f"<h3 style='margin-bottom:5px;'>7-Day Meal Plan</h3>", unsafe_allow_html=True)
            st.markdown(f"<p style='color:#8a8f9d;margin-bottom:20px;'>Tailored to your <b>{goal}</b> goal. Each meal is calculated to hit your <b>{plan['calorie_target']} kcal</b> daily target.</p>", unsafe_allow_html=True)

            for day_plan in plan["diet_plan"]:
                day = day_plan["day"]
                with st.expander(f"📅 {day}  —  {day_plan['total_cal']} kcal total", expanded=(day == "Monday")):
                    dc1, dc2 = st.columns(2)
                    with dc1:
                        b = day_plan["breakfast"]
                        st.markdown(
                            f'<div class="premium-card">'
                            f'<div style="display:flex;justify-content:space-between;align-items:center;">'
                            f'<div class="metric-label" style="color:#fee440;">🌅 BREAKFAST</div>'
                            f'<span style="color:#fee440;font-weight:700;">{day_plan["breakfast_cal"]} kcal</span></div>'
                            f'<div style="font-size:1.05rem;font-weight:700;color:#fff;margin:8px 0;">{b["name"]}</div>'
                            f'<div style="color:#9499b8;font-size:0.85rem;">{b["desc"]}</div>'
                            f'<div style="display:flex;gap:12px;margin-top:12px;">'
                            f'<span style="color:#ffb199;font-size:0.8rem;">🥩 {b.get("protein",0)}g protein</span>'
                            f'<span style="color:#00f5d4;font-size:0.8rem;">🌾 {b.get("carbs",0)}g carbs</span>'
                            f'<span style="color:#96c93d;font-size:0.8rem;">🫒 {b.get("fat",0)}g fat</span>'
                            f'</div></div>',
                            unsafe_allow_html=True
                        )
                        s = day_plan["snack"]
                        st.markdown(
                            f'<div class="premium-card">'
                            f'<div style="display:flex;justify-content:space-between;align-items:center;">'
                            f'<div class="metric-label" style="color:#9b5de5;">🍎 SNACK</div>'
                            f'<span style="color:#9b5de5;font-weight:700;">{day_plan["snack_cal"]} kcal</span></div>'
                            f'<div style="font-size:1.05rem;font-weight:700;color:#fff;margin:8px 0;">{s["name"]}</div>'
                            f'<div style="color:#9499b8;font-size:0.85rem;">{s["desc"]}</div>'
                            f'</div>',
                            unsafe_allow_html=True
                        )
                    with dc2:
                        l = day_plan["lunch"]
                        st.markdown(
                            f'<div class="premium-card">'
                            f'<div style="display:flex;justify-content:space-between;align-items:center;">'
                            f'<div class="metric-label" style="color:#00f5d4;">☀️ LUNCH</div>'
                            f'<span style="color:#00f5d4;font-weight:700;">{day_plan["lunch_cal"]} kcal</span></div>'
                            f'<div style="font-size:1.05rem;font-weight:700;color:#fff;margin:8px 0;">{l["name"]}</div>'
                            f'<div style="color:#9499b8;font-size:0.85rem;">{l["desc"]}</div>'
                            f'<div style="display:flex;gap:12px;margin-top:12px;">'
                            f'<span style="color:#ffb199;font-size:0.8rem;">🥩 {l.get("protein",0)}g protein</span>'
                            f'<span style="color:#00f5d4;font-size:0.8rem;">🌾 {l.get("carbs",0)}g carbs</span>'
                            f'<span style="color:#96c93d;font-size:0.8rem;">🫒 {l.get("fat",0)}g fat</span>'
                            f'</div></div>',
                            unsafe_allow_html=True
                        )
                        d = day_plan["dinner"]
                        st.markdown(
                            f'<div class="premium-card">'
                            f'<div style="display:flex;justify-content:space-between;align-items:center;">'
                            f'<div class="metric-label" style="color:#f77f00;">🌙 DINNER</div>'
                            f'<span style="color:#f77f00;font-weight:700;">{day_plan["dinner_cal"]} kcal</span></div>'
                            f'<div style="font-size:1.05rem;font-weight:700;color:#fff;margin:8px 0;">{d["name"]}</div>'
                            f'<div style="color:#9499b8;font-size:0.85rem;">{d["desc"]}</div>'
                            f'<div style="display:flex;gap:12px;margin-top:12px;">'
                            f'<span style="color:#ffb199;font-size:0.8rem;">🥩 {d.get("protein",0)}g protein</span>'
                            f'<span style="color:#00f5d4;font-size:0.8rem;">🌾 {d.get("carbs",0)}g carbs</span>'
                            f'<span style="color:#96c93d;font-size:0.8rem;">🫒 {d.get("fat",0)}g fat</span>'
                            f'</div></div>',
                            unsafe_allow_html=True
                        )

        # ── TAB 2: WORKOUT PLAN ────────────────────────────────────────────────
        with tab2:
            wp = plan["workout_plan"]
            st.markdown(f"<h3 style='margin-bottom:5px;'>Weekly Workout Schedule</h3>", unsafe_allow_html=True)
            st.markdown(f"<p style='color:#8a8f9d;margin-bottom:5px;'>Style: <b style='color:#9b5de5;'>{archetype}</b> — {wp['description']}</p>", unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)

            for day_workout in wp["days"]:
                day = day_workout["day"]
                focus = day_workout["focus"]
                exercises = day_workout["exercises"]
                is_rest = "Rest" in focus

                with st.expander(f"{'😴' if is_rest else '🏋️'} {day} — {focus}", expanded=(day == "Monday")):
                    if is_rest:
                        st.markdown('<div class="premium-card" style="text-align:center;padding:30px;"><div style="font-size:2rem;">😴</div><div style="font-size:1.1rem;color:#9499b8;margin-top:10px;">Rest & Recovery Day</div><div style="color:#555a7a;font-size:0.85rem;margin-top:8px;">Your muscles grow during rest. Use this day to recover, sleep well, and hydrate.</div></div>', unsafe_allow_html=True)
                    else:
                        header = '<div class="premium-card"><table style="width:100%;border-collapse:collapse;">'
                        header += '<tr style="border-bottom:1px solid rgba(255,255,255,0.08);"><th style="text-align:left;color:#9499b8;font-size:0.75rem;text-transform:uppercase;padding:8px 4px;">Exercise</th><th style="text-align:center;color:#9499b8;font-size:0.75rem;text-transform:uppercase;padding:8px;">Sets</th><th style="text-align:center;color:#9499b8;font-size:0.75rem;text-transform:uppercase;padding:8px;">Reps / Duration</th><th style="text-align:center;color:#9499b8;font-size:0.75rem;text-transform:uppercase;padding:8px;">Rest</th></tr>'
                        rows = ""
                        for i, ex in enumerate(exercises):
                            bg = "rgba(255,255,255,0.02)" if i % 2 == 0 else "transparent"
                            rows += f'<tr style="background:{bg};border-bottom:1px solid rgba(255,255,255,0.04);"><td style="padding:10px 4px;color:#f0f2ff;font-weight:500;">{ex["name"]}</td><td style="text-align:center;color:#9b5de5;font-weight:700;padding:10px;">{ex["sets"]}</td><td style="text-align:center;color:#00f5d4;font-weight:600;padding:10px;">{ex["reps"]}</td><td style="text-align:center;color:#fee440;padding:10px;">{ex["rest"]}</td></tr>'
                        st.markdown(header + rows + "</table></div>", unsafe_allow_html=True)

        # ── TAB 3: HYDRATION ───────────────────────────────────────────────────
        with tab3:
            st.markdown(f"<h3 style='margin-bottom:5px;'>Daily Hydration Schedule</h3>", unsafe_allow_html=True)
            st.markdown(f"<p style='color:#8a8f9d;margin-bottom:20px;'>Your daily water target: <b style='color:#00f5d4;'>{plan['water_target']} Liters</b> — spread optimally across the day.</p>", unsafe_allow_html=True)

            hcols = st.columns(2)
            for i, slot in enumerate(plan["hydration_schedule"]):
                col = hcols[i % 2]
                with col:
                    st.markdown(
                        f'<div class="premium-card" style="display:flex;align-items:center;gap:16px;padding:16px 20px;">'
                        f'<div style="background:linear-gradient(135deg,rgba(0,245,212,0.15),rgba(0,187,249,0.1));border-radius:12px;padding:10px 14px;text-align:center;min-width:70px;">'
                        f'<div style="color:#00f5d4;font-size:1rem;font-weight:800;">{slot["amount"]}L</div>'
                        f'<div style="color:#9499b8;font-size:0.7rem;">{slot["time"]}</div>'
                        f'</div>'
                        f'<div style="color:#c8d0e8;font-size:0.9rem;">{slot["note"]}</div>'
                        f'</div>',
                        unsafe_allow_html=True
                    )

            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown(
                '<div class="info-alert">💧 <b>Pro Tip:</b> Start every morning with 350ml of water before coffee or food. This kickstarts your metabolism and rehydrates your body after sleep.</div>',
                unsafe_allow_html=True
            )

        # ── TAB 4: DAILY ROUTINE ──────────────────────────────────────────────
        with tab4:
            st.markdown(f"<h3 style='margin-bottom:5px;'>Your Ideal Daily Routine</h3>", unsafe_allow_html=True)
            st.markdown(f"<p style='color:#8a8f9d;margin-bottom:20px;'>A structured day-plan designed around your fitness goal and lifestyle.</p>", unsafe_allow_html=True)

            for item in plan["daily_routine"]:
                time_val = item["time"]
                activity = item["activity"]
                detail = item["detail"]
                is_sleep = "Sleep" in activity
                is_workout = "Workout" in activity
                border_color = "#9b5de5" if is_sleep else ("#00f5d4" if is_workout else "rgba(255,255,255,0.1)")

                st.markdown(
                    f'<div style="display:flex;gap:16px;align-items:flex-start;margin-bottom:12px;">'
                    f'<div style="background:rgba(0,245,212,0.08);border:1px solid rgba(0,245,212,0.2);border-radius:10px;padding:8px 12px;text-align:center;min-width:90px;">'
                    f'<div style="color:#00f5d4;font-size:0.85rem;font-weight:700;">{time_val}</div>'
                    f'</div>'
                    f'<div style="background:rgba(18,20,35,0.6);border:1px solid {border_color};border-radius:12px;padding:12px 18px;flex:1;">'
                    f'<div style="font-size:1rem;font-weight:600;color:#f0f2ff;margin-bottom:4px;">{activity}</div>'
                    f'<div style="font-size:0.85rem;color:#9499b8;">{detail}</div>'
                    f'</div></div>',
                    unsafe_allow_html=True
                )
