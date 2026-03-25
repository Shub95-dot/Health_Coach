"""
Comprehensive Exercise Database for Health & Fitness Chatbot
Contains exercises categorized by movement pattern, equipment, and difficulty
"""

from typing import Dict, List
from dataclasses import dataclass


@dataclass
class Exercise:
    """Represents a single exercise"""
    name: str
    movement_pattern: str  # squat, hinge, push, pull, carry, core
    equipment: List[str]  # bodyweight, barbell, dumbbell, kettlebell, band, machine
    difficulty: str  # beginner, intermediate, advanced
    primary_muscles: List[str]
    regions_to_avoid: List[str]  # knee, shoulder, back, ankle, wrist, neck
    
    
class ExerciseDatabase:
    """Central repository of all exercises"""
    
    # Squat Pattern
    SQUATS = [
        Exercise("Bodyweight squat", "squat", ["bodyweight"], "beginner", 
                ["quads", "glutes"], []),
        Exercise("Goblet squat", "squat", ["dumbbell", "kettlebell"], "beginner",
                ["quads", "glutes"], []),
        Exercise("Box squat", "squat", ["barbell", "box"], "intermediate",
                ["quads", "glutes"], []),
        Exercise("Back squat", "squat", ["barbell"], "intermediate",
                ["quads", "glutes", "core"], ["knee"]),
        Exercise("Front squat", "squat", ["barbell"], "advanced",
                ["quads", "core"], ["knee"]),
        Exercise("Bulgarian split squat", "squat", ["dumbbell", "bodyweight"], "intermediate",
                ["quads", "glutes"], []),
        Exercise("Pistol squat", "squat", ["bodyweight"], "advanced",
                ["quads", "glutes", "core"], ["knee"]),
        Exercise("Leg press", "squat", ["machine"], "beginner",
                ["quads", "glutes"], []),
        Exercise("Hack squat", "squat", ["machine"], "intermediate",
                ["quads"], ["knee"]),
    ]
    
    # Hinge Pattern
    HINGES = [
        Exercise("Romanian deadlift", "hinge", ["barbell", "dumbbell"], "beginner",
                ["hamstrings", "glutes", "lower back"], []),
        Exercise("Conventional deadlift", "hinge", ["barbell"], "intermediate",
                ["hamstrings", "glutes", "back"], ["back"]),
        Exercise("Sumo deadlift", "hinge", ["barbell"], "intermediate",
                ["hamstrings", "glutes", "adductors"], []),
        Exercise("Trap bar deadlift", "hinge", ["trap bar"], "beginner",
                ["hamstrings", "quads", "glutes"], []),
        Exercise("Good morning", "hinge", ["barbell", "band"], "intermediate",
                ["hamstrings", "glutes", "lower back"], ["back"]),
        Exercise("Hip thrust", "hinge", ["barbell", "bodyweight"], "beginner",
                ["glutes"], []),
        Exercise("Glute bridge", "hinge", ["bodyweight", "barbell"], "beginner",
                ["glutes"], []),
        Exercise("Single leg RDL", "hinge", ["dumbbell", "bodyweight"], "intermediate",
                ["hamstrings", "glutes"], []),
        Exercise("Nordic curl", "hinge", ["bodyweight"], "advanced",
                ["hamstrings"], ["knee"]),
    ]
    
    # Push Pattern (Horizontal)
    HORIZONTAL_PUSH = [
        Exercise("Push-up", "push_horizontal", ["bodyweight"], "beginner",
                ["chest", "triceps", "shoulders"], []),
        Exercise("Incline push-up", "push_horizontal", ["bodyweight"], "beginner",
                ["chest", "triceps"], []),
        Exercise("Decline push-up", "push_horizontal", ["bodyweight"], "intermediate",
                ["chest", "triceps"], []),
        Exercise("Bench press", "push_horizontal", ["barbell"], "intermediate",
                ["chest", "triceps", "shoulders"], ["shoulder"]),
        Exercise("Dumbbell bench press", "push_horizontal", ["dumbbell"], "intermediate",
                ["chest", "triceps", "shoulders"], []),
        Exercise("Incline bench press", "push_horizontal", ["barbell", "dumbbell"], "intermediate",
                ["upper chest", "shoulders"], ["shoulder"]),
        Exercise("Dips", "push_horizontal", ["bodyweight"], "intermediate",
                ["chest", "triceps"], ["shoulder"]),
        Exercise("Cable chest press", "push_horizontal", ["cable"], "beginner",
                ["chest", "triceps"], []),
    ]
    
    # Push Pattern (Vertical)
    VERTICAL_PUSH = [
        Exercise("Pike push-up", "push_vertical", ["bodyweight"], "intermediate",
                ["shoulders", "triceps"], []),
        Exercise("Overhead press", "push_vertical", ["barbell"], "intermediate",
                ["shoulders", "triceps"], ["shoulder"]),
        Exercise("Dumbbell shoulder press", "push_vertical", ["dumbbell"], "beginner",
                ["shoulders", "triceps"], ["shoulder"]),
        Exercise("Landmine press", "push_vertical", ["barbell"], "beginner",
                ["shoulders"], []),
        Exercise("Arnold press", "push_vertical", ["dumbbell"], "intermediate",
                ["shoulders"], ["shoulder"]),
        Exercise("Handstand push-up", "push_vertical", ["bodyweight"], "advanced",
                ["shoulders", "triceps"], ["shoulder"]),
    ]
    
    # Pull Pattern (Horizontal)
    HORIZONTAL_PULL = [
        Exercise("Inverted row", "pull_horizontal", ["bodyweight"], "beginner",
                ["back", "biceps"], []),
        Exercise("Barbell row", "pull_horizontal", ["barbell"], "intermediate",
                ["back", "biceps"], ["back"]),
        Exercise("Dumbbell row", "pull_horizontal", ["dumbbell"], "beginner",
                ["back", "biceps"], []),
        Exercise("Cable row", "pull_horizontal", ["cable"], "beginner",
                ["back", "biceps"], []),
        Exercise("T-bar row", "pull_horizontal", ["barbell"], "intermediate",
                ["back", "biceps"], []),
        Exercise("Chest supported row", "pull_horizontal", ["dumbbell", "machine"], "beginner",
                ["back", "biceps"], []),
    ]
    
    # Pull Pattern (Vertical)
    VERTICAL_PULL = [
        Exercise("Pull-up", "pull_vertical", ["bodyweight"], "intermediate",
                ["lats", "biceps"], []),
        Exercise("Chin-up", "pull_vertical", ["bodyweight"], "intermediate",
                ["lats", "biceps"], []),
        Exercise("Assisted pull-up", "pull_vertical", ["machine"], "beginner",
                ["lats", "biceps"], []),
        Exercise("Lat pulldown", "pull_vertical", ["cable"], "beginner",
                ["lats", "biceps"], []),
        Exercise("Straight arm pulldown", "pull_vertical", ["cable"], "beginner",
                ["lats"], []),
    ]
    
    # Core
    CORE = [
        Exercise("Plank", "core", ["bodyweight"], "beginner",
                ["abs", "core"], []),
        Exercise("Side plank", "core", ["bodyweight"], "beginner",
                ["obliques", "core"], []),
        Exercise("Dead bug", "core", ["bodyweight"], "beginner",
                ["abs", "core"], ["back"]),
        Exercise("Bird dog", "core", ["bodyweight"], "beginner",
                ["core", "back"], []),
        Exercise("Pallof press", "core", ["cable", "band"], "beginner",
                ["core", "obliques"], []),
        Exercise("Ab wheel rollout", "core", ["ab wheel"], "advanced",
                ["abs", "core"], ["back"]),
        Exercise("Hanging leg raise", "core", ["bodyweight"], "intermediate",
                ["abs"], []),
        Exercise("Cable crunch", "core", ["cable"], "beginner",
                ["abs"], []),
    ]
    
    # Accessory - Arms
    ARMS = [
        Exercise("Bicep curl", "accessory", ["dumbbell", "barbell"], "beginner",
                ["biceps"], []),
        Exercise("Hammer curl", "accessory", ["dumbbell"], "beginner",
                ["biceps", "forearms"], []),
        Exercise("Tricep pushdown", "accessory", ["cable"], "beginner",
                ["triceps"], []),
        Exercise("Overhead tricep extension", "accessory", ["dumbbell"], "beginner",
                ["triceps"], ["shoulder"]),
        Exercise("Skull crusher", "accessory", ["barbell"], "intermediate",
                ["triceps"], []),
    ]
    
    # Accessory - Shoulders
    SHOULDER_ACCESSORY = [
        Exercise("Lateral raise", "accessory", ["dumbbell"], "beginner",
                ["shoulders"], ["shoulder"]),
        Exercise("Front raise", "accessory", ["dumbbell"], "beginner",
                ["shoulders"], ["shoulder"]),
        Exercise("Rear delt fly", "accessory", ["dumbbell"], "beginner",
                ["rear delts"], []),
        Exercise("Face pull", "accessory", ["cable"], "beginner",
                ["rear delts", "upper back"], []),
    ]
    
    # Accessory - Legs
    LEG_ACCESSORY = [
        Exercise("Leg extension", "accessory", ["machine"], "beginner",
                ["quads"], ["knee"]),
        Exercise("Leg curl", "accessory", ["machine"], "beginner",
                ["hamstrings"], []),
        Exercise("Calf raise", "accessory", ["bodyweight", "machine"], "beginner",
                ["calves"], []),
        Exercise("Hip abduction", "accessory", ["machine", "band"], "beginner",
                ["glutes"], []),
        Exercise("Hip adduction", "accessory", ["machine", "band"], "beginner",
                ["adductors"], []),
    ]
    
    # Cardio
    CARDIO = [
        Exercise("Walking", "cardio", ["bodyweight"], "beginner",
                ["cardiovascular"], []),
        Exercise("Jogging", "cardio", ["bodyweight"], "beginner",
                ["cardiovascular"], ["knee"]),
        Exercise("Running", "cardio", ["bodyweight"], "intermediate",
                ["cardiovascular"], ["knee"]),
        Exercise("Cycling", "cardio", ["bike"], "beginner",
                ["cardiovascular"], []),
        Exercise("Rowing", "cardio", ["rower"], "beginner",
                ["cardiovascular", "back"], []),
        Exercise("Jump rope", "cardio", ["rope"], "intermediate",
                ["cardiovascular", "calves"], ["knee", "ankle"]),
        Exercise("Stair climbing", "cardio", ["bodyweight"], "beginner",
                ["cardiovascular", "legs"], ["knee"]),
    ]
    
    @classmethod
    def get_all_exercises(cls) -> List[Exercise]:
        """Return all exercises in database"""
        return (cls.SQUATS + cls.HINGES + cls.HORIZONTAL_PUSH + 
                cls.VERTICAL_PUSH + cls.HORIZONTAL_PULL + cls.VERTICAL_PULL +
                cls.CORE + cls.ARMS + cls.SHOULDER_ACCESSORY + 
                cls.LEG_ACCESSORY + cls.CARDIO)
    
    @classmethod
    def get_by_pattern(cls, pattern: str) -> List[Exercise]:
        """Get exercises by movement pattern"""
        pattern_map = {
            "squat": cls.SQUATS,
            "hinge": cls.HINGES,
            "push_horizontal": cls.HORIZONTAL_PUSH,
            "push_vertical": cls.VERTICAL_PUSH,
            "pull_horizontal": cls.HORIZONTAL_PULL,
            "pull_vertical": cls.VERTICAL_PULL,
            "core": cls.CORE,
            "accessory": cls.ARMS + cls.SHOULDER_ACCESSORY + cls.LEG_ACCESSORY,
            "cardio": cls.CARDIO,
        }
        return pattern_map.get(pattern, [])
    
    @classmethod
    def get_by_equipment(cls, equipment: str) -> List[Exercise]:
        """Get exercises that use specific equipment"""
        return [ex for ex in cls.get_all_exercises() 
                if equipment.lower() in [e.lower() for e in ex.equipment]]
    
    @classmethod
    def get_by_difficulty(cls, difficulty: str) -> List[Exercise]:
        """Get exercises by difficulty level"""
        return [ex for ex in cls.get_all_exercises() 
                if ex.difficulty.lower() == difficulty.lower()]
    
    @classmethod
    def get_safe_for_injury(cls, injury_region: str) -> List[Exercise]:
        """Get exercises safe for specific injury region"""
        return [ex for ex in cls.get_all_exercises()
                if injury_region.lower() not in [r.lower() for r in ex.regions_to_avoid]]
