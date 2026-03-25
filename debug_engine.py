
from workout_engine import WorkoutProgrammer
from exercise_database import ExerciseDatabase

def test_ppl_advanced():
    programmer = WorkoutProgrammer()
    
    # Simulate advanced gym strength user
    goal = "strength"
    experience = "advanced"
    location = "gym"
    
    exercises = programmer.select_exercises(goal, experience, location)
    
    print(f"Goal: {goal}, Exp: {experience}, Loc: {location}")
    print("\nExercises Selected:")
    for k, v in exercises.items():
        print(f"  {k}: {[ex.name for ex in v]}")
        
    print("\n--- GENERATING DAYS ---")
    for day in range(1, 6): # Advanced = 5 days
        print(f"\nDAY {day}:")
        output = programmer._generate_session(
            exercises, day, "push_pull_legs", week=1, goal=goal, experience=experience
        )
        print(output)

if __name__ == "__main__":
    test_ppl_advanced()
