"""
Complete Injury Adaptation Engine
Intelligently modifies workouts to work around injuries safely
"""

from typing import List, Dict, Optional
from dataclasses import dataclass
from exercise_database import Exercise, ExerciseDatabase


@dataclass
class InjuryStatus:
    """Detailed injury status"""
    region: str  # knee, shoulder, back, ankle, wrist, neck
    severity: str  # green, yellow, red
    description: str
    pain_level: Optional[int] = None  # 1-10
    diagnosed: bool = False


class InjuryAdaptationEngine:
    """
    Intelligently modifies exercise programs to work around injuries
    Replaces problematic exercises with safe, effective alternatives
    """
    
    # Exercises to AVOID for each injury region
    REGION_BLOCKS = {
        "knee": {
            "blocked_exercises": [
                "jump squat", "box jump", "jump", "plyometric",
                "running", "heavy squat", "deep squat", 
                "pistol squat", "lunge", "bulgarian split squat",
                "leg extension", "heavy leg press", "jump rope"
            ],
            "blocked_patterns": ["jump", "run", "plyo"]
        },
        
        "shoulder": {
            "blocked_exercises": [
                "overhead press", "military press", "shoulder press",
                "snatch", "upright row", "heavy bench press",
                "handstand push-up", "dips", "overhead squat"
            ],
            "blocked_patterns": ["overhead", "heavy press"]
        },
        
        "back": {
            "blocked_exercises": [
                "heavy deadlift", "conventional deadlift",
                "good morning", "heavy barbell row",
                "heavy squat", "loaded carry heavy"
            ],
            "blocked_patterns": ["heavy compound", "max effort"]
        },
        
        "ankle": {
            "blocked_exercises": [
                "running", "jump rope", "box jump",
                "calf raise heavy", "jump squat", "sprinting"
            ],
            "blocked_patterns": ["jump", "run", "high impact"]
        },
        
        "wrist": {
            "blocked_exercises": [
                "barbell bench press", "front squat",
                "clean", "snatch", "handstand push-up",
                "barbell row", "barbell curl"
            ],
            "blocked_patterns": ["barbell", "wrist flexion"]
        },
        
        "neck": {
            "blocked_exercises": [
                "barbell squat", "overhead press heavy",
                "heavy shrugs", "upright row"
            ],
            "blocked_patterns": ["heavy overhead", "neck loading"]
        }
    }
    
    # SAFE alternatives for each injury region
    REGION_REPLACEMENTS = {
        "knee": {
            "hinge_pattern": [
                "Romanian deadlift",
                "Single leg RDL",
                "Hip thrust",
                "Glute bridge",
                "Good morning (light)"
            ],
            "quad_pattern": [
                "Leg extension (light, controlled)",
                "Terminal knee extension",
                "Step-ups (low step)",
                "Sled push",
                "Wall sit isometric"
            ],
            "cardio": [
                "Cycling",
                "Swimming",
                "Rowing machine",
                "Elliptical",
                "Walking incline"
            ]
        },
        
        "shoulder": {
            "push_pattern": [
                "Landmine press",
                "Floor press",
                "Cable chest press (neutral grip)",
                "Push-up (controlled)",
                "Incline bench press (moderate)"
            ],
            "accessory": [
                "Face pull",
                "Band pull-apart",
                "Lateral raise (light)",
                "Y-W-T raises",
                "Scapular wall slides"
            ]
        },
        
        "back": {
            "hinge_pattern": [
                "Glute bridge",
                "Hip thrust",
                "Reverse hyper (light)",
                "Bird dog",
                "Dead bug"
            ],
            "core": [
                "Plank variations",
                "McGill big 3",
                "Pallof press",
                "Side plank"
            ],
            "pull_pattern": [
                "Chest supported row",
                "Cable row",
                "Lat pulldown"
            ]
        },
        
        "ankle": {
            "lower_body": [
                "Leg press",
                "Romanian deadlift",
                "Hip thrust",
                "Leg curl",
                "Glute-ham raise"
            ],
            "cardio": [
                "Cycling",
                "Swimming",
                "Upper body ergometer",
                "Rowing machine"
            ]
        },
        
        "wrist": {
            "push_pattern": [
                "Dumbbell bench press",
                "Push-up",
                "Cable chest press",
                "Machine press",
                "Dips (if tolerated)"
            ],
            "pull_pattern": [
                "Dumbbell row",
                "Cable row",
                "Machine row",
                "Lat pulldown"
            ],
            "lower_body": [
                "Goblet squat",
                "Dumbbell RDL",
                "Leg press",
                "Machine work"
            ]
        },
        
        "neck": {
            "squat_pattern": [
                "Front squat (light)",
                "Goblet squat",
                "Leg press",
                "Dumbbell squat"
            ],
            "upper_body": [
                "Dumbbell press",
                "Machine press",
                "Cable exercises",
                "Bodyweight movements"
            ]
        }
    }
    
    def __init__(self):
        self.exercise_db = ExerciseDatabase()
    
    def modify_exercise_list(
        self, 
        exercises: List[str], 
        injury: InjuryStatus
    ) -> Dict[str, any]:
        """
        Modify an exercise list to work around an injury
        
        Args:
            exercises: List of exercise names
            injury: InjuryStatus object with region and severity
            
        Returns:
            Dict with modified exercises, removed count, added count
        """
        
        if injury.severity == "green" or not injury.region:
            # No modification needed
            return {
                "modified_exercises": exercises,
                "removed_exercises": [],
                "added_exercises": [],
                "removed_count": 0,
                "added_count": 0
            }
        
        region = injury.region.lower()
        
        if region not in self.REGION_BLOCKS:
            # Unknown region - return original
            return {
                "modified_exercises": exercises,
                "removed_exercises": [],
                "added_exercises": [],
                "removed_count": 0,
                "added_count": 0
            }
        
        blocked_info = self.REGION_BLOCKS[region]
        blocked_exercises = blocked_info["blocked_exercises"]
        blocked_patterns = blocked_info["blocked_patterns"]
        
        # Identify exercises to remove
        removed_exercises = []
        safe_exercises = []
        
        for exercise in exercises:
            exercise_lower = exercise.lower()
            
            # Check if exercise is blocked
            is_blocked = False
            
            # Check exact match
            if any(blocked in exercise_lower for blocked in blocked_exercises):
                is_blocked = True
            
            # Check pattern match
            if any(pattern in exercise_lower for pattern in blocked_patterns):
                is_blocked = True
            
            if is_blocked:
                removed_exercises.append(exercise)
            else:
                safe_exercises.append(exercise)
        
        # Add safe alternatives
        replacements = self.REGION_REPLACEMENTS.get(region, {})
        added_exercises = []
        
        # Add 2-3 alternatives per removed exercise pattern
        num_to_add = min(len(removed_exercises), 3)
        
        for pattern_name, replacement_list in replacements.items():
            for replacement in replacement_list[:num_to_add]:
                if replacement not in safe_exercises and replacement not in added_exercises:
                    added_exercises.append(replacement)
                    safe_exercises.append(replacement)
        
        return {
            "modified_exercises": safe_exercises,
            "removed_exercises": removed_exercises,
            "added_exercises": added_exercises,
            "removed_count": len(removed_exercises),
            "added_count": len(added_exercises)
        }
    
    def get_safe_exercise_database(self, injury: InjuryStatus) -> List[Exercise]:
        """
        Get filtered exercise database with only safe exercises for injury
        
        Args:
            injury: InjuryStatus object
            
        Returns:
            List of Exercise objects safe for the injury
        """
        
        if injury.severity == "green" or not injury.region:
            return self.exercise_db.get_all_exercises()
        
        # Get exercises safe for injury from database
        safe_exercises = self.exercise_db.get_safe_for_injury(injury.region)
        
        # Additional filtering based on blocked patterns
        if injury.region in self.REGION_BLOCKS:
            blocked_info = self.REGION_BLOCKS[injury.region]
            blocked_exercises = blocked_info["blocked_exercises"]
            
            # Filter out blocked exercises
            safe_exercises = [
                ex for ex in safe_exercises
                if not any(blocked in ex.name.lower() for blocked in blocked_exercises)
            ]
        
        return safe_exercises
    
    def suggest_alternatives(self, blocked_exercise: str, injury_region: str) -> List[str]:
        """
        Suggest specific alternatives for a blocked exercise
        
        Args:
            blocked_exercise: Name of the exercise that's blocked
            injury_region: The injured body region
            
        Returns:
            List of suggested alternative exercises
        """
        
        # Determine the movement pattern of the blocked exercise
        exercise_lower = blocked_exercise.lower()
        
        # Simple pattern detection
        if any(word in exercise_lower for word in ["squat", "lunge"]):
            pattern = "squat_pattern"
        elif any(word in exercise_lower for word in ["deadlift", "hinge", "rdl"]):
            pattern = "hinge_pattern"
        elif any(word in exercise_lower for word in ["press", "push"]):
            pattern = "push_pattern"
        elif any(word in exercise_lower for word in ["row", "pull"]):
            pattern = "pull_pattern"
        elif any(word in exercise_lower for word in ["run", "jog", "cardio"]):
            pattern = "cardio"
        else:
            pattern = "lower_body"  # default
        
        # Get replacements for this region and pattern
        replacements = self.REGION_REPLACEMENTS.get(injury_region, {})
        
        if pattern in replacements:
            return replacements[pattern][:3]  # Return top 3 alternatives
        
        # If pattern not found, return general alternatives
        all_alts = []
        for alt_list in replacements.values():
            all_alts.extend(alt_list[:2])
        
        return all_alts[:3]
    
    def create_modification_summary(
        self, 
        modification_result: Dict,
        injury: InjuryStatus
    ) -> str:
        """
        Create a human-readable summary of modifications
        
        Args:
            modification_result: Result from modify_exercise_list
            injury: InjuryStatus object
            
        Returns:
            Natural language summary
        """
        
        removed = modification_result["removed_count"]
        added = modification_result["added_count"]
        
        if removed == 0:
            return f"✅ Good news! All exercises in your program are safe for your {injury.region}.\n"
        
        summary = f"🩹 I've modified your program to protect your {injury.region}:\n\n"
        summary += f"❌ Removed {removed} exercises that could aggravate your injury:\n"
        
        for ex in modification_result["removed_exercises"][:5]:  # Show max 5
            summary += f"   • {ex}\n"
        
        if len(modification_result["removed_exercises"]) > 5:
            summary += f"   • ... and {len(modification_result['removed_exercises']) - 5} more\n"
        
        summary += f"\n✅ Added {added} safe, effective alternatives:\n"
        
        for ex in modification_result["added_exercises"][:5]:
            summary += f"   • {ex}\n"
        
        if len(modification_result["added_exercises"]) > 5:
            summary += f"   • ... and {len(modification_result['added_exercises']) - 5} more\n"
        
        summary += f"\n💪 You'll still make great progress while protecting your {injury.region}!\n"
        
        return summary
