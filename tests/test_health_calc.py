# fitai/tests/test_health_calc.py
# tests/test_health_calc.py
# WHY TESTS: Catch bugs before they reach users. 
# Also proves to interviewers you think like an engineer, not a script kiddie.

import pytest
from models.user_profile import UserProfile, Gender, DietType, ActivityLevel, FitnessGoal
from utils.health_calc import get_macro_split, get_water_intake_liters, get_health_summary


# Fixture = reusable test data. pytest injects it automatically into test functions.
@pytest.fixture
def sample_profile():
    return UserProfile(
        name="Nandini Kumari",
        age=22,
        gender=Gender.FEMALE,
        weight_kg=60,
        height_cm=165,
        diet_type=DietType.VEGETARIAN,
        activity_level=ActivityLevel.MODERATE,
        fitness_goal=FitnessGoal.WEIGHT_LOSS
    )


def test_bmi_calculation(sample_profile):
    # 60 / (1.65^2) = 22.0
    assert 21.0 <= sample_profile.bmi <= 23.0


def test_bmi_category(sample_profile):
    assert sample_profile.bmi_category == "Normal weight"


def test_calorie_target_weight_loss(sample_profile):
    # Weight loss = TDEE - 500, must be positive
    assert sample_profile.calorie_target > 0
    assert sample_profile.calorie_target == sample_profile.tdee - 500


def test_macro_split_adds_up(sample_profile):
    macros = get_macro_split(sample_profile)
    total_pct = macros["protein_pct"] + macros["carbs_pct"] + macros["fat_pct"]
    assert total_pct == 100


def test_water_intake_reasonable(sample_profile):
    water = get_water_intake_liters(sample_profile)
    assert 1.5 <= water <= 5.0


def test_name_formatting():
    # Test that name gets title-cased
    profile = UserProfile(
        name="nandini kumari", age=22, gender=Gender.FEMALE,
        weight_kg=60, height_cm=165, diet_type=DietType.VEGETARIAN,
        activity_level=ActivityLevel.MODERATE, fitness_goal=FitnessGoal.WEIGHT_LOSS
    )
    assert profile.name == "Nandini Kumari"


def test_invalid_age_rejected():
    # Pydantic should raise ValidationError for age=5 (below minimum of 10)
    with pytest.raises(Exception):
        UserProfile(
            name="Test", age=5, gender=Gender.FEMALE,
            weight_kg=60, height_cm=165, diet_type=DietType.VEGETARIAN,
            activity_level=ActivityLevel.MODERATE, fitness_goal=FitnessGoal.WEIGHT_LOSS
        )
