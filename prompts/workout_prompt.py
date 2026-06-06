# fitai/prompts/workout_prompt.py
# prompts/workout_prompt.py

from langchain_core.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate

WORKOUT_SYSTEM_PROMPT = """You are CoachAI, an elite certified personal trainer and sports scientist.
You design evidence-based workout programs tailored to individual fitness levels and goals.

STRICT RULES:
1. Never recommend exercises that could worsen stated medical conditions
2. Match workout intensity to activity level
3. Always include warm-up and cool-down
4. Provide sets, reps, and rest times for every exercise
5. Return ONLY valid JSON — no extra text, no markdown

You are motivating, precise, and always safety-first."""

WORKOUT_HUMAN_PROMPT = """Design a personalized weekly workout plan for:

USER PROFILE:
- Name: {name}
- Age: {age} | Gender: {gender}  
- Weight: {weight_kg}kg | BMI: {bmi} ({bmi_category})
- Activity Level: {activity_level}
- Fitness Goal: {fitness_goal}
- Medical Conditions: {diseases}

Return ONLY this JSON structure:
{{
  "weekly_plan": {{
    "monday": {{"focus": "...", "duration_mins": 45, "exercises": [{{"name": "...", "sets": 3, "reps": "12", "rest_seconds": 60, "instructions": "..."}}], "warm_up": "...", "cool_down": "..."}},
    "tuesday": {{"focus": "Rest/Active Recovery", "duration_mins": 20, "exercises": [{{"name": "Light Walk", "sets": 1, "reps": "20 mins", "rest_seconds": 0, "instructions": "Easy pace"}}], "warm_up": "None", "cool_down": "Stretching"}},
    "wednesday": {{"focus": "...", "duration_mins": 45, "exercises": [{{"name": "...", "sets": 3, "reps": "12", "rest_seconds": 60, "instructions": "..."}}], "warm_up": "...", "cool_down": "..."}},
    "thursday": {{"focus": "Rest/Active Recovery", "duration_mins": 20, "exercises": [{{"name": "Light Walk", "sets": 1, "reps": "20 mins", "rest_seconds": 0, "instructions": "Easy pace"}}], "warm_up": "None", "cool_down": "Stretching"}},
    "friday": {{"focus": "...", "duration_mins": 45, "exercises": [{{"name": "...", "sets": 3, "reps": "12", "rest_seconds": 60, "instructions": "..."}}], "warm_up": "...", "cool_down": "..."}},
    "saturday": {{"focus": "...", "duration_mins": 30, "exercises": [{{"name": "...", "sets": 2, "reps": "15", "rest_seconds": 45, "instructions": "..."}}], "warm_up": "...", "cool_down": "..."}},
    "sunday": {{"focus": "Complete Rest", "duration_mins": 0, "exercises": [], "warm_up": "None", "cool_down": "None"}}
  }},
  "weekly_summary": {{"total_workout_days": 4, "total_mins": 0, "primary_focus": "..."}},
  "pro_tips": ["tip1", "tip2", "tip3"]
}}"""

workout_prompt = ChatPromptTemplate.from_messages([
    SystemMessagePromptTemplate.from_template(WORKOUT_SYSTEM_PROMPT),
    HumanMessagePromptTemplate.from_template(WORKOUT_HUMAN_PROMPT)
])
