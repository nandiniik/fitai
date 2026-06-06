# fitai/prompts/diet_prompt.py
# prompts/diet_prompt.py
# WHY SEPARATE PROMPT FILES: Prompts are like templates — they change often.
# Keeping them separate means you can improve AI output without touching logic code.
# This is called "separation of concerns" — a core software engineering principle.

from langchain_core.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate

# SYSTEM MESSAGE: Sets the AI's role and behaviour for the entire conversation.
# Think of it as the "job description" you give to the AI.
# WHY THIS MATTERS: Without a system prompt, the AI gives generic answers.
# With a good system prompt, it behaves like a specialized expert.
DIET_SYSTEM_PROMPT = """You are Dr. NutriAI, an expert clinical nutritionist and dietitian with 15 years of experience.
You specialize in personalized Indian diet planning.

STRICT RULES:
1. Always recommend foods appropriate for the user's diet type (veg/non-veg/vegan)
2. Respect all allergies — NEVER suggest foods the user is allergic to
3. Consider medical conditions when making recommendations
4. All calorie targets must match the provided TDEE and goal
5. Prefer regional Indian foods when region is specified
6. Return ONLY valid JSON — no extra text, no markdown, no explanation

You are precise, evidence-based, and always prioritize the user's health."""

# HUMAN MESSAGE: The actual request with user data filled in.
# {curly_braces} are LangChain template variables — filled at runtime.
DIET_HUMAN_PROMPT = """Generate a personalized 1-day diet plan for:

USER PROFILE:
- Name: {name}
- Age: {age} | Gender: {gender}
- Weight: {weight_kg}kg | Height: {height_cm}cm
- BMI: {bmi} ({bmi_category})
- Diet Type: {diet_type}
- Region: {region}
- Medical Conditions: {diseases}
- Allergies: {allergies}
- Fitness Goal: {fitness_goal}

NUTRITION TARGETS:
- Daily Calories: {calorie_target} kcal
- Protein: {protein_target_g}g
- Carbs: {carbs_g}g
- Fat: {fat_g}g
- Water: {water_liters}L

Return ONLY this JSON structure:
{{
  "meals": {{
    "early_morning": {{"time": "6:30 AM", "items": [{{"name": "...", "quantity": "...", "calories": 0, "protein_g": 0}}]}},
    "breakfast": {{"time": "8:00 AM", "items": [{{"name": "...", "quantity": "...", "calories": 0, "protein_g": 0}}]}},
    "mid_morning": {{"time": "11:00 AM", "items": [{{"name": "...", "quantity": "...", "calories": 0, "protein_g": 0}}]}},
    "lunch": {{"time": "1:00 PM", "items": [{{"name": "...", "quantity": "...", "calories": 0, "protein_g": 0}}]}},
    "evening_snack": {{"time": "4:30 PM", "items": [{{"name": "...", "quantity": "...", "calories": 0, "protein_g": 0}}]}},
    "dinner": {{"time": "8:00 PM", "items": [{{"name": "...", "quantity": "...", "calories": 0, "protein_g": 0}}]}}
  }},
  "daily_totals": {{"calories": 0, "protein_g": 0, "carbs_g": 0, "fat_g": 0}},
  "hydration_tip": "...",
  "key_nutrition_tips": ["tip1", "tip2", "tip3"]
}}"""

# ChatPromptTemplate combines system + human messages into one template
# WHY: LangChain uses this to properly format messages for chat models (GPT, Llama etc.)
diet_prompt = ChatPromptTemplate.from_messages([
    SystemMessagePromptTemplate.from_template(DIET_SYSTEM_PROMPT),
    HumanMessagePromptTemplate.from_template(DIET_HUMAN_PROMPT)
])
