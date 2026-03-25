"""
Enhanced Workout Engine with Progressive Overload and Periodization
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from exercise_database import ExerciseDatabase, Exercise
from exceptions import PlanGenerationError


# Constants
GOALS = {"fat loss", "muscle gain", "weight gain", "endurance", "flexibility", "general health", "strength"}
DURATIONS = {4, 8, 12, 16, 20, 24}
LOCATIONS = {"home", "gym"}
EXPERIENCE_LEVELS = {"beginner", "intermediate", "advanced"}


class HealthCalculator:
    """Calculate health metrics for personalized programming"""
    
    @staticmethod
    def calculate_bmi(weight_kg: float, height_cm: float) -> float:
        """Calculate Body Mass Index"""
        if not weight_kg or not height_cm or height_cm == 0:
            return 22.0
        height_m = height_cm / 100
        return weight_kg / (height_m ** 2)
    
    @staticmethod
    def get_bmi_category(bmi: float) -> str:
        """Categorize BMI value"""
        if bmi < 18.5:
            return "Underweight"
        elif 18.5 <= bmi <= 25:
            return "Normal"
        elif 25 < bmi <= 30:
            return "Overweight"
        else:
            return "Obese"
    
    @staticmethod
    def estimate_max_hr(age: int) -> int:
        """Estimate maximum heart rate"""
        return 220 - age if age else 190
    
    @staticmethod
    def estimate_hr_zones(age: int) -> Dict[str, str]:
        """Calculate heart rate training zones"""
        max_hr = HealthCalculator.estimate_max_hr(age)
        return {
            "Zone 1 (Recovery)": f"{int(max_hr * 0.5)}-{int(max_hr * 0.6)} bpm",
            "Zone 2 (Fat Burn)": f"{int(max_hr * 0.6)}-{int(max_hr * 0.7)} bpm",
            "Zone 3 (Aerobic)": f"{int(max_hr * 0.7)}-{int(max_hr * 0.8)} bpm",
            "Zone 4 (Threshold)": f"{int(max_hr * 0.8)}-{int(max_hr * 0.9)} bpm",
            "Zone 5 (Max)": f"{int(max_hr * 0.9)}-{max_hr} bpm"
        }
    
    @staticmethod
    def estimate_bmr(weight_kg: float, height_cm: float, age: int, gender: str) -> float:
        """Calculate Basal Metabolic Rate using Mifflin-St Jeor"""
        if not all([weight_kg, height_cm, age]):
            return 1800
        
        bmr = 10 * weight_kg + 6.25 * height_cm - 5 * age
        if gender and gender.lower().startswith("m"):
            bmr += 5
        else:
            bmr -= 161
        return bmr
    
    @staticmethod
    def estimate_tdee(bmr: float, experience: str, goal: Optional[str] = None) -> int:
        """Calculate Total Daily Energy Expenditure"""
        if not bmr:
            return 2500
        
        # Activity multipliers based on training experience
        multipliers = {
            "beginner": 1.4,      # 3-4 days/week
            "intermediate": 1.6,  # 4-5 days/week
            "advanced": 1.8       # 5-6 days/week
        }
        return int(bmr * multipliers.get(experience, 1.5))
    
    @staticmethod
    def get_calorie_target(tdee: int, goal: str) -> int:
        """Calculate calorie target based on goal"""
        adjustments = {
            "fat loss": -500,
            "muscle gain": +300,
            "weight gain": +500,
            "strength": +200,
            "endurance": -200,
            "general health": 0
        }
        return tdee + adjustments.get(goal, 0)
    
    @staticmethod
    def get_macro_split(goal: str, calories: int) -> Dict[str, float]:
        """Calculate macronutrient targets (percentages)"""
        # Protein: 4 cal/g, Carbs: 4 cal/g, Fat: 9 cal/g
        splits = {
            "muscle gain": {"protein": 0.30, "carbs": 0.45, "fat": 0.25},
            "fat loss": {"protein": 0.40, "carbs": 0.30, "fat": 0.30},
            "strength": {"protein": 0.30, "carbs": 0.50, "fat": 0.20},
            "endurance": {"protein": 0.20, "carbs": 0.55, "fat": 0.25},
            "general health": {"protein": 0.25, "carbs": 0.45, "fat": 0.30}
        }
        
        split = splits.get(goal, splits["general health"])
        
        # Calculate macros: Protein is better served via bodyweight targets, 
        # but we provide a percentage-based fallback if weight isn't known.
        # This function primarily returns percentage-based splits for caloric balance.
        return {
            "protein_pct": split["protein"],
            "carbs_pct": split["carbs"],
            "fat_pct": split["fat"]
        }


class ProfileParser:
    """Parse user input to extract profile information"""
    
    @staticmethod
    def parse_free_text(message: str) -> Dict[str, Any]:
        """Extract profile data from natural language"""
        profile: Dict[str, Any] = {}
        msg = message.lower()
        
        # Age parsing
        age_match = re.search(r"(age\s*)?(\d{2})\s*(years|yrs|yo|year)?", msg)
        if age_match:
            profile["age"] = int(age_match.group(2))
        
        # Height parsing (cm)
        cm_match = re.search(r"(\d{3})\s*cm", msg)
        if cm_match:
            profile["height_cm"] = int(cm_match.group(1))
        
        # Height parsing (meters)
        m_match = re.search(r"(\d\.\d{1,2})\s*m", msg)
        if m_match:
            profile["height_cm"] = int(float(m_match.group(1)) * 100)
        
        # Height parsing (feet/inches)
        ft_in_match = re.search(r"(\d)'(\d{1,2})", msg)
        if ft_in_match:
            feet = int(ft_in_match.group(1))
            inches = int(ft_in_match.group(2))
            profile["height_cm"] = int((feet * 12 + inches) * 2.54)
        
        # Weight parsing (kg)
        kg_match = re.search(r"(\d{2,3})\s*kg", msg)
        if kg_match:
            profile["weight_kg"] = int(kg_match.group(1))
        
        # Weight parsing (lbs)
        lbs_match = re.search(r"(\d{2,3})\s*lbs?", msg)
        if lbs_match:
            profile["weight_kg"] = int(int(lbs_match.group(1)) * 0.453592)
        
        # Experience level
        for level in EXPERIENCE_LEVELS:
            if level in msg:
                profile["experience"] = level
                break
        
        # Goal parsing
        for goal in GOALS:
            if goal in msg:
                profile["goal"] = goal
                break
        
        # Location
        if "gym" in msg:
            profile["location"] = "gym"
        elif "home" in msg:
            profile["location"] = "home"
        
        # Duration
        weeks_match = re.search(r"(\d+)\s*weeks?", msg)
        if weeks_match:
            profile["duration_weeks"] = int(weeks_match.group(1))
        
        # Time per session
        time_match = re.search(r"(\d+)\s*(minutes?|mins?)", msg)
        if time_match:
            profile["time_minutes"] = int(time_match.group(1))
        
        # Gender
        if any(word in msg for word in ["male", "man", "guy"]):
            profile["sex"] = "male"
        elif any(word in msg for word in ["female", "woman", "girl"]):
            profile["sex"] = "female"
        
        return profile


class WorkoutProgrammer:
    """Generate structured workout programs with progressive overload"""
    
    def __init__(self):
        self.exercise_db = ExerciseDatabase()
    
    def select_exercises(self, 
                        goal: str, 
                        experience: str, 
                        location: str,
                        injury_region: Optional[str] = None) -> Dict[str, List[Exercise]]:
        """Select exercises based on criteria with difficulty scaling"""
        
        # Normalize
        goal = goal.lower() if goal else "general health"
        experience = experience.lower() if experience else "beginner"
        location = location.lower() if location else "gym"
        injury_region_lower = injury_region.lower() if injury_region else None
        
        # Difficulty scaling
        levels_map = {
            "beginner": ["beginner"],
            "intermediate": ["beginner", "intermediate"],
            "advanced": ["beginner", "intermediate", "advanced"]
        }
        allowed_levels = levels_map.get(experience, ["beginner"])
        
        # Get all exercises and filter
        all_exercises = self.exercise_db.get_all_exercises()
        available = [ex for ex in all_exercises if ex.difficulty in allowed_levels]
        
        # Filter by equipment
        if location == "home":
            available = [ex for ex in available 
                        if any(equip in ["bodyweight", "band", "dumbbell"] for equip in ex.equipment)]
        
        # Filter by injury
        if injury_region_lower:
            available = [ex for ex in available
                        if injury_region_lower not in [r.lower() for r in ex.regions_to_avoid]]
        
        # Select exercises by pattern
        selected = {
            "squat": self._select_from_pattern(available, "squat", 2),
            "hinge": self._select_from_pattern(available, "hinge", 2),
            "push_horizontal": self._select_from_pattern(available, "push_horizontal", 2),
            "push_vertical": self._select_from_pattern(available, "push_vertical", 1),
            "pull_horizontal": self._select_from_pattern(available, "pull_horizontal", 2),
            "pull_vertical": self._select_from_pattern(available, "pull_vertical", 1),
            "core": self._select_from_pattern(available, "core", 3),
        }
        
        # Add accessories based on goal
        if goal in ["muscle gain", "strength", "muscle_gain"]:
            selected["accessory"] = self._select_from_pattern(available, "accessory", 4)
        
        # Final safety check: if a critical pattern is empty, try to steal from 'all'
        # [BUG FIX]: Ensure fallback also respects injury_region
        for pattern in ["squat", "push_horizontal", "pull_horizontal"]:
            if not selected[pattern]:
                pattern_fallback = [ex for ex in all_exercises 
                                   if ex.movement_pattern == pattern and 
                                   (not injury_region or injury_region.lower() not in [r.lower() for r in ex.regions_to_avoid])]
                if pattern_fallback:
                    selected[pattern] = pattern_fallback[:1]
        
        return selected
    
    def _select_from_pattern(self, available: List[Exercise], pattern: str, count: int) -> List[Exercise]:
        """Select exercises from a specific pattern"""
        pattern_exercises = [ex for ex in available if ex.movement_pattern == pattern]
        return pattern_exercises[:count] if len(pattern_exercises) >= count else pattern_exercises
    
    def generate_week(self, 
                     exercises: Dict[str, List[Exercise]],
                     week_number: int,
                     goal: str,
                     experience: str,
                     sessions_per_week: int = 3) -> str:
        """Generate a single week of training"""
        
        week_output = f"\n=== WEEK {week_number} ===\n"
        
        # Normalize
        goal = goal.lower()
        experience = experience.lower()
        
        # Determine split based on sessions per week
        if sessions_per_week <= 3:
            split_type = "full_body"
        elif sessions_per_week == 4:
            split_type = "upper_lower"
        else:
            split_type = "push_pull_legs"
        
        # Generate sessions
        for day in range(1, sessions_per_week + 1):
            week_output += self._generate_session(
                exercises, day, split_type, week_number, goal, experience
            )
        
        return week_output
    
    def _generate_session(self,
                         exercises: Dict[str, List[Exercise]],
                         day: int,
                         split_type: str,
                         week: int,
                         goal: str,
                         experience: str) -> str:
        """Generate a single training session"""
        
        output = f"\nDay {day}:\n"
        output += "Warm-up:\n"
        output += "  - 5-10 min dynamic mobility\n"
        output += "  - Movement prep specific to today's patterns\n\n"
        
        output += "Main Work:\n"
        
        # Volume and intensity progression
        sets, reps, intensity = self._get_programming_params(week, goal, experience)
        
        if split_type == "full_body":
            # Full body: hit all patterns
            for pattern in ["squat", "hinge", "push_horizontal", "pull_horizontal"]:
                if exercises.get(pattern):
                    ex = exercises[pattern][day % len(exercises[pattern])]
                    output += f"  - {ex.name}: {sets} x {reps}, rest 90-120s\n"
            
            if exercises.get("core"):
                output += f"  - {exercises['core'][0].name}: 3 x 30-45s\n"

        elif split_type == "upper_lower":
            # Day 1 & 3: Upper, Day 2 & 4: Lower
            if day % 2 == 1:  # Upper
                patterns = ["push_horizontal", "pull_horizontal", "push_vertical", "pull_vertical"]
            else:  # Lower
                patterns = ["squat", "hinge", "core"]
                
            for pattern in patterns:
                if exercises.get(pattern) and len(exercises[pattern]) > 0:
                    # Rotate exercises based on day
                    idx = (day // 2) % len(exercises[pattern])
                    ex = exercises[pattern][idx]
                    output += f"  - {ex.name}: {sets} x {reps}, rest 90-120s\n"

        elif split_type == "push_pull_legs":
            # Day 1: Push, Day 2: Pull, Day 3: Legs, then repeat or core
            if day % 3 == 1:  # Push
                patterns = ["push_horizontal", "push_vertical"]
            elif day % 3 == 2:  # Pull
                patterns = ["pull_horizontal", "pull_vertical"]
            else:  # Legs
                patterns = ["squat", "hinge"]
                
            for pattern in patterns:
                if exercises.get(pattern) and len(exercises[pattern]) > 0:
                    idx = (day // 3) % len(exercises[pattern])
                    ex = exercises[pattern][idx]
                    output += f"  - {ex.name}: {sets} x {reps}, rest 90-120s\n"
            
            # Add core on leg days
            if day % 3 == 0 and exercises.get("core"):
                output += f"  - {exercises['core'][0].name}: 3 x 45s\n"

        # Add accessories if available
        if exercises.get("accessory"):
            # Select 1-2 accessories based on the day's focus
            acc_idx = day % len(exercises["accessory"])
            output += f"  - Accessory: {exercises['accessory'][acc_idx].name}: 3 x 12-15 reps\n"
        
        output += "\nCool-down:\n"
        output += "  - 5 min light cardio\n"
        output += "  - Static stretching 5-10 min\n"
        
        return output
    
    def _get_programming_params(self, week: int, goal: str, experience: str) -> tuple:
        """Determine sets, reps, and intensity based on week and goal"""
        
        # Progressive overload scheme
        if goal == "strength":
            if week <= 3:
                return (4, "5-6", "80-85%")
            elif week <= 6:
                return (5, "3-5", "85-90%")
            else:
                return (3, "1-3", "90-95%")
        
        elif goal == "muscle gain":
            if week <= 4:
                return (3, "8-12", "70-75%")
            elif week <= 8:
                return (4, "8-12", "75-80%")
            else:
                return (4, "6-10", "80-85%")
        
        elif goal == "fat loss":
            return (3, "12-15", "65-70%")
        
        elif goal == "endurance":
            return (3, "15-20", "50-60%")
        
        else:  # general health
            return (3, "10-12", "70%")


class PlanGenerator:
    """Main plan generation class"""
    
    def __init__(self):
        self.programmer = WorkoutProgrammer()
        self.health_calc = HealthCalculator()
    
    def generate_multiweek_plan(self, profile, params: Dict[str, Any]) -> str:
        """Generate complete multi-week training plan"""
        
        # Extract parameters with defaults
        goal = params.get("goal", getattr(profile, "goal", "general health"))
        duration_weeks = params.get("duration_weeks", getattr(profile, "duration_weeks", 8))
        experience = params.get("experience", getattr(profile, "experience", "beginner"))
        location = params.get("location", getattr(profile, "location", "gym"))
        time_minutes = params.get("time_minutes", getattr(profile, "time_minutes", 60))
        
        # Get injury region if exists
        injury_region = getattr(profile, "injury_region", None)
        
        # Generate nutrition recommendations
        output = self._generate_nutrition_section(profile, goal)
        
        # Select exercises
        exercises = self.programmer.select_exercises(
            goal, experience, location, injury_region
        )
        
        # Validate we have exercises
        if not any(exercises.values()):
            raise PlanGenerationError("Unable to select appropriate exercises for profile")
        
        # Generate weeks
        output += f"\n{'='*60}\n"
        output += f"TRAINING PROGRAM: {duration_weeks} WEEKS\n"
        output += f"Goal: {goal.upper()}\n"
        output += f"Experience: {experience.upper()}\n"
        output += f"Location: {location.upper()}\n"
        output += f"{'='*60}\n"
        
        # Determine sessions per week based on experience (case-insensitive)
        exp_lower = experience.lower()
        sessions_per_week = {"beginner": 3, "intermediate": 4, "advanced": 5}.get(exp_lower, 3)
        
        # Generate each week
        for week in range(1, duration_weeks + 1):
            is_deload = (week % 4 == 0)
            if is_deload:
                output += f"\n=== WEEK {week} (DELOAD) ===\n"
                output += "Focus: Recovery and Technique. reduce all weights by 20-30% and sets by 1.\n"
                
            output += self.programmer.generate_week(
                exercises, week, goal, experience, sessions_per_week
            )
        
        # Add closing notes
        output += self._generate_closing_notes(goal, experience)
        
        return output
    
    def _generate_nutrition_section(self, profile, goal: str) -> str:
        """Generate personalized nutrition recommendations"""
        
        output = "\n=== NUTRITION GUIDELINES ===\n"
        
        # Calculate metrics if we have data
        weight = getattr(profile, "weight_kg", None)
        height = getattr(profile, "height_cm", None)
        age = getattr(profile, "age", None)
        sex = getattr(profile, "sex", None)
        experience = getattr(profile, "experience", "intermediate")
        
        if weight and height:
            bmi = self.health_calc.calculate_bmi(weight, height)
            output += f"Current BMI: {bmi:.1f} ({self.health_calc.get_bmi_category(bmi)})\n"
        
        if all([weight, height, age, sex]):
            bmr = self.health_calc.estimate_bmr(weight, height, age, sex)
            tdee = self.health_calc.estimate_tdee(bmr, experience, goal)
            calories = self.health_calc.get_calorie_target(tdee, goal)
            macros = self.health_calc.get_macro_split(goal, calories)
            
            output += f"\nDaily Calorie Target: {calories} kcal\n"
            
            # Use bodyweight-based protein for more professional accuracy
            # 1.6 - 2.2 g/kg is the scientific gold standard for most trainees
            protein_target_g = int(weight * 2.0) if goal in ["muscle gain", "strength"] else int(weight * 2.2) if goal == "fat loss" else int(weight * 1.6)
            
            remaining_cal = calories - (protein_target_g * 4)
            fat_cal = calories * macros['fat_pct']
            fat_g = int(fat_cal / 9)
            carb_cal = remaining_cal - fat_cal
            carb_g = int(carb_cal / 4)
            
            output += f"Protein: {protein_target_g}g (approx. {protein_target_g/weight:.1f}g/kg)\n"
            output += f"Carbs: {carb_g}g | Fat: {fat_g}g\n"
        
        # General recommendations
        output += f"\nGeneral Guidelines for {goal}:\n"
        if goal == "muscle gain":
            output += "  - Prioritize protein (1.6-2.2g per kg bodyweight)\n"
            output += "  - Eat in slight caloric surplus (+300-500 kcal)\n"
            output += "  - Time protein around workouts\n"
        elif goal == "fat loss":
            output += "  - Maintain high protein (2.0-2.5g per kg bodyweight)\n"
            output += "  - Moderate caloric deficit (-500 kcal)\n"
            output += "  - Focus on whole foods, high satiety\n"
        elif goal == "strength":
            output += "  - Adequate protein (1.8-2.2g per kg bodyweight)\n"
            output += "  - Sufficient carbs for performance\n"
            output += "  - Maintain or slight surplus\n"
        
        output += "\n"
        return output
    
    def _generate_closing_notes(self, goal: str, experience: str) -> str:
        """Generate closing notes and recommendations"""
        
        notes = f"\n\n{'='*60}\n"
        notes += "PROGRAM NOTES:\n"
        notes += "- Track all workouts and progressively increase weight/reps\n"
        notes += "- Prioritize sleep (7-9 hours) and recovery\n"
        notes += "- Stay hydrated (3-4 liters/day)\n"
        notes += "- Listen to your body - scale back if needed\n"
        
        if experience == "beginner":
            notes += "- Focus on form over weight\n"
            notes += "- Take extra rest days if sore\n"
        
        notes += f"\n{'='*60}\n"
        
        return notes
