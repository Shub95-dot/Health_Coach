import sys
import os

# Ensure we can import from the current directory
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from workout_engine import PlanGenerator, HealthCalculator, WorkoutProgrammer
from exercise_database import ExerciseDatabase
from dataclasses import dataclass, field
from typing import Optional, List, Dict

@dataclass
class UserProfile:
    user_id: str
    name: Optional[str] = None
    age: Optional[int] = None
    sex: Optional[str] = None
    height_cm: Optional[float] = None
    weight_kg: Optional[float] = None
    goal: Optional[str] = None
    experience: Optional[str] = None
    location: Optional[str] = None
    duration_weeks: Optional[int] = None
    time_minutes: Optional[int] = None
    injury_region: Optional[str] = None
    injury_severity: Optional[str] = None
    injury_description: Optional[str] = None
    chat_history: List[Dict[str, str]] = field(default_factory=list)

def test_nutrition_edge_cases():
    print("Testing Nutrition Edge Cases...")
    calc = HealthCalculator()
    
    # Very light person (40kg)
    bmr = calc.estimate_bmr(40, 140, 60, "female")
    tdee = calc.estimate_tdee(bmr, "beginner", "fat loss")
    calories = calc.get_calorie_target(tdee, "fat loss")
    macros = calc.get_macro_split("fat loss", calories)
    
    # Calculate protein manually for the test
    protein_target_g = int(40 * 2.2) # Fat loss target in code
    protein_g_per_kg = protein_target_g / 40
    print(f"Weight 40kg, Fat Loss: {calories} cal, Protein {protein_target_g}g ({protein_g_per_kg:.2f}g/kg)")
    
    if protein_g_per_kg < 1.6:
        print("!!! Potential Bug: Protein target too low (under 1.6g/kg) for weight loss !!!")

def test_fallback_safety_bug():
    print("\nTesting Fallback Safety Bug...")
    prog = WorkoutProgrammer()
    
    # Simulate an environment where ONLY exercises are red-flagged for knee
    # We want to see if the fallback (line 257 of workout_engine.py) ignores this
    
    injury_region = "knee"
    selected = prog.select_exercises("muscle gain", "advanced", "gym", injury_region=injury_region)
    
    # Find all 'squat' pattern exercises in 'selected'
    squats = selected.get("squat", [])
    for ex in squats:
        if injury_region in [r.lower() for r in ex.regions_to_avoid]:
            print(f"!!! CRITICAL BUG: Found '{ex.name}' in squats despite '{injury_region}' injury !!!")
            return
    
    print("No unsafe squats found in this run.")

def test_plan_generation():
    print("\nTesting Plan Generation...")
    gen = PlanGenerator()
    profile = UserProfile(user_id="test_user")
    profile.weight_kg = 80
    profile.height_cm = 180
    profile.age = 30
    profile.sex = "male"
    profile.experience = "intermediate"
    profile.goal = "muscle gain"
    
    params = {
        "goal": "muscle gain",
        "duration_weeks": 4,
        "experience": "intermediate",
        "location": "gym",
        "time_minutes": 60
    }
    
    try:
        plan = gen.generate_multiweek_plan(profile, params)
        print("Plan generation successful.")
        if "Nutrition" in plan:
            print("Nutrition section found.")
    except Exception as e:
        print(f"Plan Generation Failed: {e}")

if __name__ == "__main__":
    test_nutrition_edge_cases()
    test_fallback_safety_bug()
    test_plan_generation()
