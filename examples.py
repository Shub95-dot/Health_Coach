"""
Example Usage and Test Cases for Health & Fitness Chatbot
Demonstrates various use cases and functionality
"""

from workout_engine import PlanGenerator, ProfileParser, HealthCalculator
from exercise_database import ExerciseDatabase
from exceptions import MedicalReferralRequired


def example_1_basic_muscle_gain():
    """Example: Basic muscle gain program for intermediate gym user"""
    print("\n" + "="*60)
    print("EXAMPLE 1: Muscle Gain Program")
    print("="*60)
    
    # Create a mock profile
    class Profile:
        user_id = "user123"
        age = 25
        sex = "male"
        weight_kg = 75
        height_cm = 180
        goal = "muscle gain"
        experience = "intermediate"
        location = "gym"
        duration_weeks = 12
        time_minutes = 60
        injury_region = None
    
    profile = Profile()
    
    # Generate plan
    planner = PlanGenerator()
    plan = planner.generate_multiweek_plan(profile, {})
    
    print(plan[:2000])  # Print first 2000 chars
    print("\n... (truncated for brevity) ...\n")


def example_2_injury_safe_program():
    """Example: Program for someone with knee injury"""
    print("\n" + "="*60)
    print("EXAMPLE 2: Knee-Safe Program")
    print("="*60)
    
    class Profile:
        user_id = "user456"
        age = 30
        sex = "female"
        weight_kg = 65
        height_cm = 165
        goal = "fat loss"
        experience = "beginner"
        location = "home"
        duration_weeks = 8
        time_minutes = 45
        injury_region = "knee"
    
    profile = Profile()
    
    # Get safe exercises
    safe_exercises = ExerciseDatabase.get_safe_for_injury("knee")
    print(f"\nFound {len(safe_exercises)} knee-safe exercises")
    print("\nSample safe exercises:")
    for ex in safe_exercises[:5]:
        print(f"  - {ex.name} ({ex.movement_pattern})")
    
    # Generate plan
    planner = PlanGenerator()
    plan = planner.generate_multiweek_plan(profile, {})
    print("\nGenerated knee-safe program successfully!")


def example_3_parse_user_input():
    """Example: Parse natural language user input"""
    print("\n" + "="*60)
    print("EXAMPLE 3: Natural Language Parsing")
    print("="*60)
    
    test_inputs = [
        "I'm 28 years old, 180cm, 75kg, male, intermediate level",
        "I want to lose fat, I have 8 weeks, and I train at the gym",
        "Beginner, home workouts, 30 minutes per session",
        "6'2 tall, 200 lbs, looking to build muscle"
    ]
    
    parser = ProfileParser()
    
    for input_text in test_inputs:
        print(f"\nInput: {input_text}")
        parsed = parser.parse_free_text(input_text)
        print(f"Parsed: {parsed}")


def example_4_health_calculations():
    """Example: Health metric calculations"""
    print("\n" + "="*60)
    print("EXAMPLE 4: Health Calculations")
    print("="*60)
    
    calc = HealthCalculator()
    
    # Example user
    weight_kg = 75
    height_cm = 180
    age = 28
    sex = "male"
    experience = "intermediate"
    goal = "muscle gain"
    
    # Calculate metrics
    bmi = calc.calculate_bmi(weight_kg, height_cm)
    bmi_cat = calc.get_bmi_category(bmi)
    bmr = calc.estimate_bmr(weight_kg, height_cm, age, sex)
    tdee = calc.estimate_tdee(bmr, experience)
    calories = calc.get_calorie_target(tdee, goal)
    macros = calc.get_macro_split(goal, calories)
    hr_zones = calc.estimate_hr_zones(age)
    
    print(f"\nUser Stats:")
    print(f"  Weight: {weight_kg}kg")
    print(f"  Height: {height_cm}cm")
    print(f"  Age: {age}")
    print(f"  Sex: {sex}")
    print(f"\nCalculated Metrics:")
    print(f"  BMI: {bmi:.1f} ({bmi_cat})")
    print(f"  BMR: {bmr:.0f} kcal")
    print(f"  TDEE: {tdee} kcal")
    print(f"  Target Calories: {calories} kcal")
    print(f"\nMacros:")
    print(f"  Protein: {macros['protein_g']}g")
    print(f"  Carbs: {macros['carbs_g']}g")
    print(f"  Fat: {macros['fat_g']}g")
    print(f"\nHeart Rate Zones:")
    for zone, range_val in hr_zones.items():
        print(f"  {zone}: {range_val}")


def example_5_exercise_database_queries():
    """Example: Query the exercise database"""
    print("\n" + "="*60)
    print("EXAMPLE 5: Exercise Database Queries")
    print("="*60)
    
    # Get all exercises
    all_ex = ExerciseDatabase.get_all_exercises()
    print(f"\nTotal exercises in database: {len(all_ex)}")
    
    # Get by pattern
    squats = ExerciseDatabase.get_by_pattern("squat")
    print(f"\nSquat exercises: {len(squats)}")
    for ex in squats[:3]:
        print(f"  - {ex.name}")
    
    # Get by equipment
    bodyweight = ExerciseDatabase.get_by_equipment("bodyweight")
    print(f"\nBodyweight exercises: {len(bodyweight)}")
    
    dumbbell = ExerciseDatabase.get_by_equipment("dumbbell")
    print(f"Dumbbell exercises: {len(dumbbell)}")
    
    # Get by difficulty
    beginner = ExerciseDatabase.get_by_difficulty("beginner")
    advanced = ExerciseDatabase.get_by_difficulty("advanced")
    print(f"\nBeginner exercises: {len(beginner)}")
    print(f"Advanced exercises: {len(advanced)}")
    
    # Get safe for injuries
    knee_safe = ExerciseDatabase.get_safe_for_injury("knee")
    shoulder_safe = ExerciseDatabase.get_safe_for_injury("shoulder")
    print(f"\nKnee-safe exercises: {len(knee_safe)}")
    print(f"Shoulder-safe exercises: {len(shoulder_safe)}")


def example_6_program_comparison():
    """Example: Compare different program types"""
    print("\n" + "="*60)
    print("EXAMPLE 6: Program Type Comparison")
    print("="*60)
    
    class BaseProfile:
        user_id = "comparison_user"
        age = 28
        sex = "male"
        weight_kg = 75
        height_cm = 180
        experience = "intermediate"
        location = "gym"
        duration_weeks = 8
        time_minutes = 60
        injury_region = None
    
    goals = ["fat loss", "muscle gain", "strength", "endurance"]
    planner = PlanGenerator()
    
    for goal in goals:
        profile = BaseProfile()
        profile.goal = goal
        
        plan = planner.generate_multiweek_plan(profile, {})
        
        # Extract just nutrition section
        nutrition_end = plan.find("TRAINING PROGRAM")
        nutrition = plan[:nutrition_end] if nutrition_end != -1 else plan[:500]
        
        print(f"\n{goal.upper()} Program:")
        print(nutrition)


def run_all_examples():
    """Run all example use cases"""
    examples = [
        ("Basic Muscle Gain", example_1_basic_muscle_gain),
        ("Injury-Safe Program", example_2_injury_safe_program),
        ("Natural Language Parsing", example_3_parse_user_input),
        ("Health Calculations", example_4_health_calculations),
        ("Exercise Database", example_5_exercise_database_queries),
        ("Program Comparison", example_6_program_comparison),
    ]
    
    print("\n" + "="*60)
    print("HEALTH & FITNESS CHATBOT - EXAMPLES")
    print("="*60)
    
    for i, (name, func) in enumerate(examples, 1):
        try:
            func()
        except Exception as e:
            print(f"\nError in {name}: {e}")
    
    print("\n" + "="*60)
    print("All examples completed!")
    print("="*60 + "\n")


if __name__ == "__main__":
    # Run individual examples or all
    run_all_examples()
    
    # Or run specific example:
    # example_1_basic_muscle_gain()
    # example_3_parse_user_input()
    # example_4_health_calculations()
