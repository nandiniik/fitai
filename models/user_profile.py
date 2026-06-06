# fitai/models/user_profile.py
# models/user_profile.py

# Pydantic is a data validation library.
# WHY USE IT: Instead of manually checking "is age a number? is it > 0?"
# Pydantic does all of that automatically and gives clean error messages.
# It's used in FastAPI, LangChain, and almost every modern Python backend.

from pydantic import BaseModel, Field, field_validator, computed_field
from enum import Enum
from typing import Optional


# Enums restrict a field to only specific allowed values.
# WHY: If someone types "Male " or "male" or "MALE" — Enum handles it cleanly.
class Gender(str, Enum):
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"


class DietType(str, Enum):
    VEGETARIAN = "vegetarian"
    NON_VEGETARIAN = "non-vegetarian"
    VEGAN = "vegan"
    EGGETARIAN = "eggetarian"


class ActivityLevel(str, Enum):
    SEDENTARY = "sedentary"          # desk job, no exercise
    LIGHT = "light"                  # light exercise 1-3 days/week
    MODERATE = "moderate"            # moderate exercise 3-5 days/week
    ACTIVE = "active"                # hard exercise 6-7 days/week
    VERY_ACTIVE = "very_active"      # athlete / physical job


class FitnessGoal(str, Enum):
    WEIGHT_LOSS = "weight_loss"
    MUSCLE_GAIN = "muscle_gain"
    MAINTENANCE = "maintenance"
    ENDURANCE = "endurance"


# BaseModel is Pydantic's base class.
# Every field has a type annotation — Pydantic enforces these at runtime.
class UserProfile(BaseModel):
    # Field() lets us add constraints and descriptions
    name: str = Field(..., min_length=1, max_length=100, description="Full name")
    age: int = Field(..., ge=10, le=100, description="Age in years")  # ge=greater or equal, le=less or equal
    gender: Gender
    weight_kg: float = Field(..., gt=20, lt=300, description="Weight in kilograms")
    height_cm: float = Field(..., gt=100, lt=250, description="Height in centimeters")
    diet_type: DietType
    activity_level: ActivityLevel
    fitness_goal: FitnessGoal
    diseases: Optional[str] = Field(default="None", description="Any medical conditions")
    allergies: Optional[str] = Field(default="None", description="Food allergies")
    region: Optional[str] = Field(default="Indian", description="Dietary region preference")

    # field_validator lets you write custom validation logic
    # WHY: Pydantic handles type checking, but business logic needs custom validators
    @field_validator('name')
    @classmethod
    def name_must_not_be_empty(cls, v):
        if not v.strip():
            raise ValueError("Name cannot be blank")
        return v.strip().title()  # "nandini kumari" → "Nandini Kumari"

    # computed_field automatically calculates a value from other fields
    # WHY: BMI is derived from weight and height — we don't ask the user for it
    @computed_field
    @property
    def bmi(self) -> float:
        # BMI formula: weight(kg) / height(m)^2
        height_m = self.height_cm / 100
        return round(self.weight_kg / (height_m ** 2), 1)

    @computed_field
    @property
    def bmi_category(self) -> str:
        if self.bmi < 18.5:
            return "Underweight"
        elif self.bmi < 25:
            return "Normal weight"
        elif self.bmi < 30:
            return "Overweight"
        else:
            return "Obese"

    @computed_field
    @property
    def tdee(self) -> int:
        """
        TDEE = Total Daily Energy Expenditure
        WHY: This is how many calories the person burns per day.
        We use this to set calorie targets for diet recommendations.
        Formula: Mifflin-St Jeor (most accurate for general use)
        """
        # Step 1: Calculate BMR (Basal Metabolic Rate) — calories burned at rest
        if self.gender == Gender.MALE:
            bmr = 10 * self.weight_kg + 6.25 * self.height_cm - 5 * self.age + 5
        else:
            bmr = 10 * self.weight_kg + 6.25 * self.height_cm - 5 * self.age - 161

        # Step 2: Multiply by activity multiplier
        multipliers = {
            ActivityLevel.SEDENTARY: 1.2,
            ActivityLevel.LIGHT: 1.375,
            ActivityLevel.MODERATE: 1.55,
            ActivityLevel.ACTIVE: 1.725,
            ActivityLevel.VERY_ACTIVE: 1.9
        }
        return int(bmr * multipliers[self.activity_level])

    @computed_field
    @property
    def calorie_target(self) -> int:
        """Adjust TDEE based on fitness goal"""
        if self.fitness_goal == FitnessGoal.WEIGHT_LOSS:
            return self.tdee - 500   # 500 calorie deficit = ~0.5kg/week loss
        elif self.fitness_goal == FitnessGoal.MUSCLE_GAIN:
            return self.tdee + 300   # 300 calorie surplus
        else:
            return self.tdee         # maintenance

    @computed_field
    @property
    def protein_target_g(self) -> int:
        """Protein target in grams — based on goal and weight"""
        if self.fitness_goal == FitnessGoal.MUSCLE_GAIN:
            return int(self.weight_kg * 2.0)   # 2g per kg for muscle gain
        elif self.fitness_goal == FitnessGoal.WEIGHT_LOSS:
            return int(self.weight_kg * 1.6)   # higher protein prevents muscle loss
        else:
            return int(self.weight_kg * 1.2)   # general health
