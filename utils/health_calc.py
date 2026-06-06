# fitai/utils/health_calc.py
# utils/health_calc.py
# Pure utility functions — no classes, no side effects, easy to test
# WHY SEPARATE FILE: These functions are used by multiple modules.
# Keeping them here means we don't repeat code (DRY principle)

from models.user_profile import UserProfile, FitnessGoal, ActivityLevel


def get_macro_split(profile: UserProfile) -> dict:
    """
    Returns macro breakdown as percentages and grams.
    Macros = Protein, Carbohydrates, Fat
    WHY: Different goals need different macro ratios.
    """
    calories = profile.calorie_target

    if profile.fitness_goal == FitnessGoal.MUSCLE_GAIN:
        # High protein, moderate carbs for energy, moderate fat
        protein_pct, carb_pct, fat_pct = 0.30, 0.45, 0.25
    elif profile.fitness_goal == FitnessGoal.WEIGHT_LOSS:
        # High protein (preserves muscle), lower carbs, moderate fat
        protein_pct, carb_pct, fat_pct = 0.35, 0.35, 0.30
    else:
        # Balanced maintenance
        protein_pct, carb_pct, fat_pct = 0.25, 0.50, 0.25

    return {
        "protein_g": int((calories * protein_pct) / 4),   # protein = 4 cal/g
        "carbs_g": int((calories * carb_pct) / 4),        # carbs = 4 cal/g
        "fat_g": int((calories * fat_pct) / 9),           # fat = 9 cal/g
        "protein_pct": int(protein_pct * 100),
        "carbs_pct": int(carb_pct * 100),
        "fat_pct": int(fat_pct * 100),
    }


def get_water_intake_liters(profile: UserProfile) -> float:
    """
    Daily water intake recommendation.
    Base: 35ml per kg of body weight, adjusted for activity.
    """
    base = profile.weight_kg * 0.035
    activity_bonus = {
        ActivityLevel.SEDENTARY: 0,
        ActivityLevel.LIGHT: 0.3,
        ActivityLevel.MODERATE: 0.5,
        ActivityLevel.ACTIVE: 0.7,
        ActivityLevel.VERY_ACTIVE: 1.0
    }
    return round(base + activity_bonus[profile.activity_level], 1)


def get_health_summary(profile: UserProfile) -> dict:
    """Single function to get all health metrics — used by UI and PDF export"""
    macros = get_macro_split(profile)
    return {
        "bmi": profile.bmi,
        "bmi_category": profile.bmi_category,
        "tdee": profile.tdee,
        "calorie_target": profile.calorie_target,
        "protein_target_g": profile.protein_target_g,
        "water_liters": get_water_intake_liters(profile),
        **macros
    }