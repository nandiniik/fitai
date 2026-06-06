# fitai/chains/workout_chain.py
# chains/workout_chain.py

import json
import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.output_parsers import StrOutputParser
from prompts.workout_prompt import workout_prompt
from models.user_profile import UserProfile

load_dotenv()


def get_llm():
    return ChatGroq(
        model="llama-3.3-70b-versatile",
        temperature=0.4,
        max_tokens=2000,
        api_key=os.getenv("GROQ_API_KEY")
    )


def generate_workout_plan(profile: UserProfile) -> dict:
    """Takes a UserProfile, returns a structured weekly workout plan dict."""
    llm = get_llm()
    chain = workout_prompt | llm | StrOutputParser()

    input_data = {
        "name": profile.name,
        "age": profile.age,
        "gender": profile.gender.value,
        "weight_kg": profile.weight_kg,
        "bmi": profile.bmi,
        "bmi_category": profile.bmi_category,
        "activity_level": profile.activity_level.value,
        "fitness_goal": profile.fitness_goal.value,
        "diseases": profile.diseases,
    }

    try:
        raw_response = chain.invoke(input_data)
        cleaned = raw_response.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.split("```")[1]
            if cleaned.startswith("json"):
                cleaned = cleaned[4:]
        return json.loads(cleaned)
    except json.JSONDecodeError:
        return {"error": "Could not parse AI response", "raw": raw_response}
    except Exception as e:
        return {"error": str(e)}