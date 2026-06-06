# fitai/app.py - Main entry point

# app.py — Main Streamlit application entry point
# Streamlit turns Python scripts into web apps automatically.
# WHY STREAMLIT over Flask: Zero HTML/CSS needed, built-in components,
# perfect for AI/data projects, deploys free on Streamlit Cloud.

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import json

from models.user_profile import (UserProfile, Gender, DietType,
                                   ActivityLevel, FitnessGoal)
from chains.diet_chain import generate_diet_plan
from chains.workout_chain import generate_workout_plan
from utils.health_calc import get_health_summary, get_macro_split, get_water_intake_liters
from database.db import (init_db, save_user_profile,
                          save_recommendation, get_total_users_count)

# --- PAGE CONFIG (must be first Streamlit call) ---
st.set_page_config(
    page_title="FitAI — Personalized Health Platform",
    page_icon="💪",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize database on startup
init_db()

# --- CUSTOM CSS ---
st.markdown("""
<style>
    .metric-card {
        background: linear-gradient(135deg, #1a1d27, #252836);
        border: 1px solid #00C896;
        border-radius: 12px;
        padding: 20px;
        text-align: center;
        margin: 5px 0;
    }
    .metric-value { font-size: 2rem; font-weight: 700; color: #00C896; }
    .metric-label { font-size: 0.85rem; color: #aaa; margin-top: 4px; }
    .meal-card {
        background: #1a1d27;
        border-left: 3px solid #00C896;
        border-radius: 8px;
        padding: 15px;
        margin: 8px 0;
    }
    .exercise-card {
        background: #1a1d27;
        border-left: 3px solid #ff6b35;
        border-radius: 8px;
        padding: 15px;
        margin: 8px 0;
    }
    .stButton > button {
        background: linear-gradient(135deg, #00C896, #00a87a);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 12px 30px;
        font-size: 1rem;
        font-weight: 600;
        width: 100%;
    }
    .hero-title {
        font-size: 2.5rem;
        font-weight: 800;
        background: linear-gradient(135deg, #00C896, #00a87a);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
</style>
""", unsafe_allow_html=True)


# ============================================================
# SIDEBAR — Navigation
# ============================================================
with st.sidebar:
    st.markdown("### 💪 FitAI")
    st.markdown("*AI-Powered Health Platform*")
    st.divider()

    page = st.radio("Navigate", [
        "🏠 Home",
        "📋 Get My Plan",
        "📊 Dashboard"
    ], label_visibility="collapsed")

    st.divider()
    total = get_total_users_count()
    st.markdown(f"**{total}** plans generated so far")
    st.markdown("---")
    st.markdown("Built with LangChain + Groq")


# ============================================================
# PAGE 1 — HOME
# ============================================================
if page == "🏠 Home":
    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown('<p class="hero-title">Your AI Health Coach</p>', unsafe_allow_html=True)
        st.markdown("#### Personalized diet & workout plans in under 10 seconds")
        st.markdown("""
        **What FitAI does for you:**
        - 🥗 Custom meal plans based on your body, goals & food preferences
        - 💪 Weekly workout schedules matched to your fitness level
        - 📊 Health metrics: BMI, TDEE, macro breakdown
        - 📄 Download your plan as PDF
        - 🧠 Powered by Llama 3.3-70B via Groq
        """)
        if st.button("🚀 Generate My Plan Now"):
            st.session_state["page_override"] = "📋 Get My Plan"
            st.rerun()

    with col2:
        # Stats cards
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{total}+</div>
            <div class="metric-label">Plans Generated</div>
        </div>
        <div class="metric-card">
            <div class="metric-value">&lt;10s</div>
            <div class="metric-label">Response Time</div>
        </div>
        <div class="metric-card">
            <div class="metric-value">100%</div>
            <div class="metric-label">Personalized</div>
        </div>
        """, unsafe_allow_html=True)


# ============================================================
# PAGE 2 — GET MY PLAN (Main Feature)
# ============================================================
elif page == "📋 Get My Plan":
    st.markdown("## 📋 Tell us about yourself")
    st.markdown("Fill in your details and we'll generate a fully personalized plan.")

    with st.form("user_profile_form"):
        # Row 1 — Basic info
        col1, col2, col3 = st.columns(3)
        with col1:
            name = st.text_input("Full Name", placeholder="Nandini Kumari")
        with col2:
            age = st.number_input("Age", min_value=10, max_value=100, value=22)
        with col3:
            gender = st.selectbox("Gender", ["female", "male", "other"])

        # Row 2 — Body measurements
        col1, col2 = st.columns(2)
        with col1:
            weight = st.number_input("Weight (kg)", min_value=20.0, max_value=300.0, value=60.0, step=0.5)
        with col2:
            height = st.number_input("Height (cm)", min_value=100.0, max_value=250.0, value=165.0, step=0.5)

        # Row 3 — Preferences
        col1, col2, col3 = st.columns(3)
        with col1:
            diet_type = st.selectbox("Diet Type", ["vegetarian", "non-vegetarian", "vegan", "eggetarian"])
        with col2:
            activity = st.selectbox("Activity Level", [
                "sedentary", "light", "moderate", "active", "very_active"
            ], index=2)
        with col3:
            goal = st.selectbox("Fitness Goal", [
                "weight_loss", "muscle_gain", "maintenance", "endurance"
            ])

        # Row 4 — Health details
        col1, col2, col3 = st.columns(3)
        with col1:
            region = st.text_input("Region/Cuisine", value="Indian")
        with col2:
            diseases = st.text_input("Medical Conditions", value="None", placeholder="diabetes, hypertension...")
        with col3:
            allergies = st.text_input("Food Allergies", value="None", placeholder="nuts, dairy...")

        submitted = st.form_submit_button("🧠 Generate My Personalized Plan")

    if submitted:
        if not name.strip():
            st.error("Please enter your name.")
        else:
            try:
                # Build validated profile
                profile = UserProfile(
                    name=name, age=age,
                    gender=Gender(gender),
                    weight_kg=weight, height_cm=height,
                    diet_type=DietType(diet_type),
                    activity_level=ActivityLevel(activity),
                    fitness_goal=FitnessGoal(goal),
                    region=region, diseases=diseases, allergies=allergies
                )
            except Exception as e:
                st.error(f"Invalid input: {e}")
                st.stop()

            # Save to database
            summary = get_health_summary(profile)
            user_id = save_user_profile({
                "name": profile.name, "age": profile.age,
                "gender": profile.gender.value,
                "weight_kg": profile.weight_kg, "height_cm": profile.height_cm,
                "diet_type": profile.diet_type.value,
                "activity_level": profile.activity_level.value,
                "fitness_goal": profile.fitness_goal.value,
                "diseases": profile.diseases, "allergies": profile.allergies,
                "region": profile.region,
                "bmi": profile.bmi, "calorie_target": profile.calorie_target
            })

            # Store in session for results display
            st.session_state["profile"] = profile
            st.session_state["summary"] = summary
            st.session_state["user_id"] = user_id
            st.session_state["show_results"] = True

    # ---- RESULTS SECTION ----
    if st.session_state.get("show_results"):
        profile = st.session_state["profile"]
        summary = st.session_state["summary"]

        st.divider()
        st.markdown(f"## ✅ Your Personalized Plan — {profile.name}")

        # --- HEALTH METRICS ROW ---
        st.markdown("### 📊 Your Health Metrics")
        c1, c2, c3, c4, c5 = st.columns(5)
        metrics = [
            (c1, "BMI", f"{summary['bmi']}", summary['bmi_category']),
            (c2, "Daily Calories", f"{summary['calorie_target']}", "kcal target"),
            (c3, "Protein Target", f"{summary['protein_target_g']}g", "per day"),
            (c4, "Water Intake", f"{summary['water_liters']}L", "per day"),
            (c5, "TDEE", f"{summary['tdee']}", "kcal burned/day"),
        ]
        for col, label, value, sub in metrics:
            with col:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-value">{value}</div>
                    <div class="metric-label">{label}<br><small>{sub}</small></div>
                </div>""", unsafe_allow_html=True)

        # --- CHARTS ROW ---
        st.markdown("### 📈 Nutrition Breakdown")
        col1, col2 = st.columns(2)

        with col1:
            # Macro pie chart
            fig = go.Figure(data=[go.Pie(
                labels=["Protein", "Carbs", "Fat"],
                values=[summary["protein_pct"], summary["carbs_pct"], summary["fat_pct"]],
                hole=0.4,
                marker_colors=["#00C896", "#4ECDC4", "#FF6B35"]
            )])
            fig.update_layout(
                title="Macro Split (%)",
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font_color="white", height=300,
                margin=dict(t=40, b=0, l=0, r=0)
            )
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            # BMI gauge
            bmi_val = summary["bmi"]
            fig2 = go.Figure(go.Indicator(
                mode="gauge+number",
                value=bmi_val,
                title={"text": f"BMI — {summary['bmi_category']}", "font": {"color": "white"}},
                gauge={
                    "axis": {"range": [10, 40], "tickcolor": "white"},
                    "bar": {"color": "#00C896"},
                    "steps": [
                        {"range": [10, 18.5], "color": "#3a86ff"},
                        {"range": [18.5, 25], "color": "#06d6a0"},
                        {"range": [25, 30], "color": "#ffbe0b"},
                        {"range": [30, 40], "color": "#ff006e"},
                    ],
                }
            ))
            fig2.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                font_color="white", height=300,
                margin=dict(t=40, b=0, l=0, r=0)
            )
            st.plotly_chart(fig2, use_container_width=True)

        # --- AI GENERATION ---
        tab1, tab2 = st.tabs(["🥗 Diet Plan", "💪 Workout Plan"])

        with tab1:
            with st.spinner("🧠 Generating your personalized diet plan..."):
                diet_plan = generate_diet_plan(profile)

            if "error" in diet_plan:
                st.error(f"Error: {diet_plan['error']}")
            else:
                st.success("✅ Diet plan generated!")
                meals = diet_plan.get("meals", {})
                meal_icons = {
                    "early_morning": "🌅", "breakfast": "🍳",
                    "mid_morning": "🍎", "lunch": "🍱",
                    "evening_snack": "☕", "dinner": "🌙"
                }
                for meal_key, meal_data in meals.items():
                    icon = meal_icons.get(meal_key, "🍽️")
                    meal_name = meal_key.replace("_", " ").title()
                    with st.expander(f"{icon} {meal_name} — {meal_data.get('time', '')}"):
                        for item in meal_data.get("items", []):
                            st.markdown(f"""
                            <div class="meal-card">
                                <strong>{item.get('name')}</strong> — {item.get('quantity')}<br>
                                <small>🔥 {item.get('calories', 0)} kcal &nbsp;|&nbsp;
                                💪 {item.get('protein_g', 0)}g protein</small>
                            </div>""", unsafe_allow_html=True)

                totals = diet_plan.get("daily_totals", {})
                st.markdown(f"""
                **Daily Totals:** 🔥 {totals.get('calories', 0)} kcal |
                💪 {totals.get('protein_g', 0)}g protein |
                🌾 {totals.get('carbs_g', 0)}g carbs |
                🥑 {totals.get('fat_g', 0)}g fat
                """)

                if diet_plan.get("key_nutrition_tips"):
                    st.markdown("**💡 Nutrition Tips:**")
                    for tip in diet_plan["key_nutrition_tips"]:
                        st.markdown(f"- {tip}")

                # Save to DB
                save_recommendation(
                    st.session_state["user_id"], profile.name,
                    diet_plan, {}
                )
                st.session_state["diet_plan"] = diet_plan

        with tab2:
            with st.spinner("🧠 Generating your personalized workout plan..."):
                workout_plan = generate_workout_plan(profile)

            if "error" in workout_plan:
                st.error(f"Error: {workout_plan['error']}")
            else:
                st.success("✅ Workout plan generated!")
                weekly = workout_plan.get("weekly_plan", {})
                day_order = ["monday","tuesday","wednesday","thursday","friday","saturday","sunday"]
                day_icons = {"monday":"💪","tuesday":"🚶","wednesday":"🏋️",
                             "thursday":"🧘","friday":"⚡","saturday":"🏃","sunday":"😴"}

                for day in day_order:
                    if day not in weekly:
                        continue
                    data = weekly[day]
                    icon = day_icons.get(day, "📅")
                    with st.expander(f"{icon} {day.title()} — {data.get('focus','Rest')} ({data.get('duration_mins',0)} mins)"):
                        if data.get("warm_up") and data["warm_up"] != "None":
                            st.markdown(f"🔥 **Warm-up:** {data['warm_up']}")
                        for ex in data.get("exercises", []):
                            st.markdown(f"""
                            <div class="exercise-card">
                                <strong>{ex.get('name')}</strong><br>
                                {ex.get('sets')} sets × {ex.get('reps')} reps |
                                Rest: {ex.get('rest_seconds', 0)}s<br>
                                <small><em>{ex.get('instructions','')}</em></small>
                            </div>""", unsafe_allow_html=True)
                        if data.get("cool_down") and data["cool_down"] != "None":
                            st.markdown(f"❄️ **Cool-down:** {data['cool_down']}")

                if workout_plan.get("pro_tips"):
                    st.markdown("**💡 Pro Tips:**")
                    for tip in workout_plan["pro_tips"]:
                        st.markdown(f"- {tip}")
                # --- PDF DOWNLOAD BUTTON ---
                st.divider()
                st.markdown("### 📄 Download Your Complete Plan")
                
                if st.session_state.get("diet_plan") and workout_plan:
                    from utils.pdf_export import generate_pdf_report
                    try:
                        pdf_bytes = generate_pdf_report(
                            profile,
                            st.session_state.get("diet_plan", {}),
                            workout_plan
                        )
                        st.download_button(
                            label="⬇️ Download PDF Report",
                            data=pdf_bytes,
                            file_name=f"FitAI_Plan_{profile.name.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.pdf",
                            mime="application/pdf",
                            use_container_width=True
                        )
                        st.caption("Your personalized diet + workout plan as a branded PDF")
                    except Exception as e:
                        st.error(f"PDF generation error: {e}")

                # Store workout for PDF
                st.session_state["workout_plan"] = workout_plan
                st.session_state["diet_plan"] = diet_plan if 'diet_plan' in dir() else {}


# ============================================================
# PAGE 3 — DASHBOARD
# ============================================================
elif page == "📊 Dashboard":
    from database.db import get_all_users
    st.markdown("## 📊 Platform Dashboard")

    users = get_all_users()
    total = len(users)

    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("Total Users", total)
    with c2:
        if users:
            avg_bmi = round(sum(u.bmi for u in users if u.bmi) / max(total, 1), 1)
            st.metric("Avg BMI", avg_bmi)
    with c3:
        if users:
            avg_cal = int(sum(u.calorie_target for u in users if u.calorie_target) / max(total, 1))
            st.metric("Avg Calorie Target", f"{avg_cal} kcal")

    if users:
        # Goal distribution chart
        goals = {}
        for u in users:
            goals[u.fitness_goal] = goals.get(u.fitness_goal, 0) + 1

        fig = px.bar(
            x=list(goals.keys()), y=list(goals.values()),
            title="Users by Fitness Goal",
            color=list(goals.values()),
            color_continuous_scale=["#00C896", "#00a87a"]
        )
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font_color="white"
        )
        st.plotly_chart(fig, use_container_width=True)

        # User table
        st.markdown("### Recent Users")
        for u in users[:10]:
            st.markdown(f"**{u.name}** | {u.age}y | BMI: {u.bmi} | Goal: {u.fitness_goal} | {u.created_at.strftime('%d %b %Y') if u.created_at else 'N/A'}")
