# fitai/chains/diet_chain.py
# chains/diet_chain.py
# A "chain" in LangChain = prompt → AI model → output parser, connected together.
# WHY CHAINS: Instead of manually calling the API, formatting input, parsing output —
# LangChain chains do all that in one clean pipeline.
# This is called LCEL (LangChain Expression Language) — the modern standard.

import json
import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
# NEW (correct):
from langchain_core.output_parsers import StrOutputParser
from prompts.diet_prompt import diet_prompt
from utils.health_calc import get_macro_split, get_water_intake_liters
from models.user_profile import UserProfile

load_dotenv()


def get_llm():
    """
    Initialize the Groq LLM.
    WHY GROQ: Fastest inference (tokens/sec) of any free provider.
    llama-3.3-70b is genuinely powerful — comparable to GPT-4o for structured tasks.
    WHY FUNCTION: Makes it easy to swap models later without changing chain code.
    """
    return ChatGroq(
        model="llama-3.3-70b-versatile",
        temperature=0.3,       # lower = more consistent/factual, higher = more creative
        max_tokens=2000,
        api_key=os.getenv("GROQ_API_KEY")
    )


def generate_diet_plan(profile: UserProfile) -> dict:
    """
    Main function: takes a UserProfile, returns a structured diet plan dict.
    
    The pipeline: prompt template → LLM → string output → JSON parse
    This is the LCEL "pipe" syntax: component1 | component2 | component3
    """
    llm = get_llm()
    macros = get_macro_split(profile)
    water = get_water_intake_liters(profile)

    # Build the chain using LCEL pipe operator
    # diet_prompt formats the template → llm generates response → StrOutputParser extracts text
    chain = diet_prompt | llm | StrOutputParser()

    # Prepare all template variables
    input_data = {
        "name": profile.name,
        "age": profile.age,
        "gender": profile.gender.value,
        "weight_kg": profile.weight_kg,
        "height_cm": profile.height_cm,
        "bmi": profile.bmi,
        "bmi_category": profile.bmi_category,
        "diet_type": profile.diet_type.value,
        "region": profile.region,
        "diseases": profile.diseases,
        "allergies": profile.allergies,
        "fitness_goal": profile.fitness_goal.value,
        "calorie_target": profile.calorie_target,
        "protein_target_g": profile.protein_target_g,
        "carbs_g": macros["carbs_g"],
        "fat_g": macros["fat_g"],
        "water_liters": water
    }

    try:
        raw_response = chain.invoke(input_data)
        # Clean response — sometimes LLMs add ```json ``` wrappers despite instructions
        cleaned = raw_response.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.split("```")[1]
            if cleaned.startswith("json"):
                cleaned = cleaned[4:]
        return json.loads(cleaned)
    except json.JSONDecodeError:
        # Fallback — return a basic structure so the app never crashes
        return {"error": "Could not parse AI response", "raw": raw_response}
    except Exception as e:
        return {"error": str(e)}