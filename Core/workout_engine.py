import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field

from injury_adaptation import InjuryAdaptationEngine


GOALS = {"fat loss", "muscle gain", "weight gain", "endurance", "flexibility", "general health"}
DURATIONS = {4, 8, 16, 24, 32}
LOCATIONS = {"home", "gym"}
EXPERIENCE_LEVELS = {"beginner", "intermediate", "advanced"}
MENSTRUAL_PHASES = {"menstrual", "follicular", "ovulatory", "luteal"}



# Health / Calculation helpers


class HealthCalculator:
    @staticmethod
    def calculate_bmi(weight_kg: Optional[float], height_cm: Optional[float]) -> float:
        if not weight_kg or not height_cm:
            return 22.0
        height_m = height_cm / 100.0
        return weight_kg / (height_m ** 2)

    @staticmethod
    def get_bmi_category(bmi: float) -> str:
        if bmi < 18.5:
            return "Underweight"
        elif 18.5 <= bmi <= 25:
            return "Normal"
        elif 25 < bmi <= 30:
            return "Overweight"
        else:
            return "Obese"

    @staticmethod
    def estimate_max_hr(age: Optional[int]) -> int:
        return 220 - age if age else 190

    @staticmethod
    def estimate_hr_zones(age: Optional[int]) -> Dict[str, str]:
        max_hr = HealthCalculator.estimate_max_hr(age)
        return {
            "Zone 1 (Recovery)": f"{int(max_hr * 0.5)}-{int(max_hr * 0.6)} bpm",
            "Zone 2 (Fat Burn)": f"{int(max_hr * 0.6)}-{int(max_hr * 0.7)} bpm",
            "Zone 3 (Aerobic)": f"{int(max_hr * 0.7)}-{int(max_hr * 0.8)} bpm",
            "Zone 4 (Max)": f"{int(max_hr * 0.9)}-{max_hr} bpm",
        }

    @staticmethod
    def estimate_bmr(weight_kg: Optional[float],
                     height_cm: Optional[float],
                     age: Optional[int],
                     gender: Optional[str]) -> float:
        if not all([weight_kg, height_cm, age]):
            return 1800.0

        bmr = 10 * weight_kg + 6.25 * height_cm - 5 * age
        if gender and gender.lower().startswith("m"):
            bmr += 5
        else:
            bmr -= 161
        return bmr

    @staticmethod
    def estimate_tdee(bmr: Optional[float], experience: Optional[str]) -> int:
        if not bmr:
            return 2500

        multipliers = {
            "beginner": 1.4,
            "intermediate": 1.6,
            "advanced": 1.8,
        }
        return int(bmr * multipliers.get(experience, 1.5))

    @staticmethod
    def get_calorie_target(tdee: int, goal: Optional[str]) -> int:
        adjustments = {
            "fat loss": -500,
            "muscle gain": +300,
            "weight gain": +500,
            "general health": 0,
        }
        return tdee + adjustments.get(goal, 0)


# ---------------------------------------------------------------------------
# Optional text parser (currently not wired to dialog)
# ---------------------------------------------------------------------------

class ProfileParser:
    """Legacy free-text parser. You can call this if you want extra extraction outside NLU."""

    @staticmethod
    def parse_free_text(message: str) -> Dict[str, Any]:
        profile: Dict[str, Any] = {}
        msg = message.lower()

        age_match = re.search(r"(age\s*)?(\d{2})\s*(years|yrs|yo|year)?", msg)
        if age_match:
            profile["age"] = int(age_match.group(2))

        cm_match = re.search(r"(\d{3})\s*cm", msg)
        if cm_match:
            profile["height_cm"] = int(cm_match.group(1))

        m_match = re.search(r"(\d\.\d{1,2})\s*m", msg)
        if m_match:
            profile["height_cm"] = int(float(m_match.group(1)) * 100)

        ft_in_match = re.search(r"(\d)'(\d{1,2})", msg)
        if ft_in_match:
            feet = int(ft_in_match.group(1))
            inches = int(ft_in_match.group(2))
            profile["height_cm"] = int((feet * 12 + inches) * 2.54)

        w = re.search(r"(\d{2,3})\s*kg", msg)
        if w:
            profile["weight_kg"] = int(w.group(1))

        for level in EXPERIENCE_LEVELS:
            if level in msg:
                profile["experience"] = level
                break

        if any(x in msg for x in ["fat loss", "lose fat", "cutting"]):
            profile["goal"] = "fat loss"
        elif any(x in msg for x in ["muscle", "hypertrophy"]):
            profile["goal"] = "muscle gain"
        elif any(x in msg for x in ["weight gain", "bulk"]):
            profile["goal"] = "weight gain"

        if "home" in msg:
            profile["location"] = "home"
        elif "gym" in msg:
            profile["location"] = "gym"

        d = re.search(r"(\d+)\s*(week|weeks|wk)", msg)
        if d:
            profile["duration_weeks"] = int(d.group(1))

        t = re.search(r"(\d{2,3})\s*(minutes|min)", msg)
        if t:
            profile["time_minutes"] = int(t.group(1))

        if any(x in msg for x in ["pregnant", "pregnancy", "prenatal"]):
            profile["pregnant"] = True

        for phase in MENSTRUAL_PHASES:
            if phase in msg:
                profile["cycle_phase"] = phase
                break

        if any(x in msg for x in ["injury", "hurt", "pain", "torn", "sprain", "fracture"]):
            profile["injury"] = message

        return profile


# ---------------------------------------------------------------------------
# Program structures
# ---------------------------------------------------------------------------

@dataclass
class ExercisePrescription:
    name: str
    sets: int
    reps: str
    tempo: str
    rest_seconds: int
    notes: str = ""


@dataclass
class DayPlan:
    day_index: int
    focus: str
    blocks: Dict[str, List[ExercisePrescription]]


@dataclass
class WeekPlan:
    week_index: int
    theme: str
    days: List[DayPlan] = field(default_factory=list)


@dataclass
class ProgramPlan:
    goal: str
    duration_weeks: int
    sessions_per_week: int
    weeks: List[WeekPlan] = field(default_factory=list)

    def to_text(self) -> str:
        lines: List[str] = []
        lines.append(f"Goal: {self.goal}")
        lines.append(f"Duration: {self.duration_weeks} weeks")
        lines.append(f"Sessions per week: {self.sessions_per_week}")
        lines.append("")

        for w in self.weeks:
            lines.append(f"=== Week {w.week_index}: {w.theme} ===")
            for d in w.days:
                lines.append(f"\nDay {d.day_index}: {d.focus}")
                for block_name, exs in d.blocks.items():
                    lines.append(f"  {block_name}:")
                    for ex in exs:
                        line = f"    - {ex.name}: {ex.sets} x {ex.reps}, tempo {ex.tempo}, rest {ex.rest_seconds}s"
                        if ex.notes:
                            line += f" ({ex.notes})"
                        lines.append(line)
            lines.append("")

        return "\n".join(lines)


# ---------------------------------------------------------------------------
# Plan generator (multi-week + quick workouts)
# ---------------------------------------------------------------------------

class PlanGenerator:
    def __init__(self, exercise_db: Optional[List[Dict[str, Any]]] = None):
        self.injury_adapter = InjuryAdaptationEngine()
        self.exercise_db = exercise_db

    # -------------- PUBLIC API --------------

    def generate_multiweek_plan(self, profile, params: Dict[str, Any]) -> str:
        """
        Currently: specialized for fat loss / recomposition.
        Other goals fall back to a generic message.
        """

        goal = (params.get("goal") or getattr(profile, "goal", None) or "").lower()
        duration_weeks = params.get("duration_weeks") or getattr(profile, "duration_weeks", None) or 8
        experience = (params.get("experience") or getattr(profile, "experience", None) or "beginner").lower()
        location = (params.get("location") or getattr(profile, "location", None) or "home").lower()
        time_minutes = params.get("time_minutes") or getattr(profile, "time_minutes", None) or 45

        try:
            duration_weeks = int(duration_weeks)
        except Exception:
            duration_weeks = 8
        try:
            time_minutes = int(time_minutes)
        except Exception:
            time_minutes = 45

        # Only fat-loss engine is fully built for now
        if ("loss" in goal) or ("cut" in goal) or ("recomp" in goal) or (goal in {"fat loss", "weight loss"}):
            program = self._build_fat_loss_program(
                duration_weeks=duration_weeks,
                experience=experience,
                location=location,
                time_minutes=time_minutes,
                profile=profile,
            )
            return program.to_text()

        return (
            "Right now I create detailed **fat loss / body recomposition** programs with full exercise, tempo, "
            "and rest prescriptions.\n"
            "For other goals (pure strength, competition prep, etc.) we’ll add dedicated engines in the next phase."
        )

    def generate_quick_workout(self, profile, params: Dict[str, Any]) -> str:
        goal = (params.get("goal") or getattr(profile, "goal", None) or "").lower()
        time_minutes = params.get("time_minutes") or getattr(profile, "time_minutes", None) or 25
        location = (params.get("location") or getattr(profile, "location", None) or "home").lower()
        experience = (params.get("experience") or getattr(profile, "experience", None) or "beginner").lower()

        try:
            time_minutes = int(time_minutes)
        except Exception:
            time_minutes = 25

        if (not goal) or ("loss" in goal) or ("cut" in goal) or ("recomp" in goal):
            return self._build_fat_loss_quick_workout(
                time_minutes=time_minutes,
                experience=experience,
                location=location,
            )

        return (
            "Here’s a general conditioning session.\n"
            "Once I have specialized engines for your exact goal, I’ll tailor it more precisely."
        )

    # -------------- INTERNAL: FAT LOSS PROGRAM --------------

    def _build_fat_loss_program(
        self,
        duration_weeks: int,
        experience: str,
        location: str,
        time_minutes: int,
        profile,
    ) -> ProgramPlan:

        duration_weeks = max(4, min(duration_weeks, 16))

        if experience == "beginner":
            sessions_per_week = 3
        elif experience == "advanced":
            sessions_per_week = 5
        else:
            sessions_per_week = 4

        program = ProgramPlan(
            goal="Fat loss / body recomposition",
            duration_weeks=duration_weeks,
            sessions_per_week=sessions_per_week,
        )

        for week_idx in range(1, duration_weeks + 1):
            if week_idx <= max(2, duration_weeks // 3):
                theme = "Foundation: technique, full-body strength, moderate conditioning"
            elif week_idx <= max(4, 2 * duration_weeks // 3):
                theme = "Progressive overload: more volume and conditioning density"
            else:
                theme = "Intensification: intervals and circuits, controlled fatigue"

            week = WeekPlan(week_index=week_idx, theme=theme)

            for day_idx in range(1, sessions_per_week + 1):
                day = self._build_fat_loss_day(
                    week_index=week_idx,
                    day_index=day_idx,
                    total_time=time_minutes,
                    experience=experience,
                    location=location,
                    profile=profile,
                )
                week.days.append(day)

            program.weeks.append(week)

        return program

    def _build_fat_loss_day(
        self,
        week_index: int,
        day_index: int,
        total_time: int,
        experience: str,
        location: str,
        profile,
    ) -> DayPlan:

        focus = "Full body strength + conditioning"
        blocks: Dict[str, List[ExercisePrescription]] = {
            "Warm-up": [],
            "Strength": [],
            "Conditioning": [],
            "Cool-down": [],
        }

        # --- Warm-up ---
        blocks["Warm-up"] = [
            ExercisePrescription(
                name="Dynamic mobility (hips, shoulders, spine)",
                sets=1,
                reps="5-8 each movement",
                tempo="controlled",
                rest_seconds=0,
                notes="Move continuously, no fatigue, prepare joints.",
            ),
            ExercisePrescription(
                name="Low-intensity cardio (walk, bike, light jog)",
                sets=1,
                reps="5-7 min",
                tempo="steady",
                rest_seconds=0,
                notes="Stay easy; you should be able to hold a conversation.",
            ),
        ]

        # --- Strength block (base) ---
        if location == "gym":
            strength_exercises = [
                ExercisePrescription(
                    name="Goblet squat or leg press",
                    sets=3 if experience == "beginner" else 4,
                    reps="10-12",
                    tempo="3-0-1-0",
                    rest_seconds=60,
                    notes="Controlled descent, drive up with power. RPE 7-8.",
                ),
                ExercisePrescription(
                    name="Dumbbell bench press or push-up",
                    sets=3 if experience == "beginner" else 4,
                    reps="10-12",
                    tempo="3-0-1-0",
                    rest_seconds=60,
                    notes="Keep shoulder blades stable, do not bounce.",
                ),
                ExercisePrescription(
                    name="Seated row or cable row",
                    sets=3 if experience == "beginner" else 4,
                    reps="10-12",
                    tempo="2-1-2-0",
                    rest_seconds=60,
                    notes="Squeeze shoulder blades, control the return.",
                ),
            ]
        else:
            strength_exercises = [
                ExercisePrescription(
                    name="Squat or split squat (bodyweight or backpack load)",
                    sets=3 if experience == "beginner" else 4,
                    reps="10-15",
                    tempo="3-0-1-0",
                    rest_seconds=60,
                    notes="Keep knees tracking over toes, spine neutral.",
                ),
                ExercisePrescription(
                    name="Push-up (incline if needed)",
                    sets=3 if experience == "beginner" else 4,
                    reps="8-12",
                    tempo="3-0-1-0",
                    rest_seconds=60,
                    notes="Stop 2 reps before failure; quality reps only.",
                ),
                ExercisePrescription(
                    name="Hip hinge (RDL or good morning with band/backpack)",
                    sets=3 if experience == "beginner" else 4,
                    reps="10-12",
                    tempo="3-1-1-0",
                    rest_seconds=60,
                    notes="Feel hamstrings load on the way down, no rounding.",
                ),
            ]

        # --- Injury adaptation on Strength block ---
        injury_region = getattr(profile, "injury_region", None)
        if injury_region:
            strength_exercises = self._adapt_strength_for_injury(strength_exercises, injury_region)

        blocks["Strength"] = strength_exercises

        # --- Conditioning ---
        if week_index <= 2:
            conditioning = [
                ExercisePrescription(
                    name="Low-impact intervals (bike, brisk walk, step-ups)",
                    sets=6,
                    reps="30s work / 30s easy",
                    tempo="steady",
                    rest_seconds=0,
                    notes="RPE ~7 on work, 3-4 on easy.",
                )
            ]
        else:
            conditioning = [
                ExercisePrescription(
                    name="Circuit: squat / push-up / row / hinge",
                    sets=3 if experience == "beginner" else 4,
                    reps="40s work / 20s transition per exercise",
                    tempo="controlled but continuous",
                    rest_seconds=60,
                    notes="Rotate between 3-4 movements with minimal rest.",
                )
            ]

        blocks["Conditioning"] = conditioning

        # --- Cool-down ---
        blocks["Cool-down"] = [
            ExercisePrescription(
                name="Walking + breathing drill",
                sets=1,
                reps="3-5 min",
                tempo="slow",
                rest_seconds=0,
                notes="Inhale through the nose, slow exhale through the mouth.",
            ),
            ExercisePrescription(
                name="Light stretching (hips, hamstrings, chest)",
                sets=1,
                reps="20-30s per area",
                tempo="static",
                rest_seconds=0,
                notes="No pain; just gentle tension.",
            ),
        ]

        return DayPlan(day_index=day_index, focus=focus, blocks=blocks)

    # -------------- INTERNAL: QUICK FAT LOSS SESSION --------------

    def _build_fat_loss_quick_workout(
        self,
        time_minutes: int,
        experience: str,
        location: str,
    ) -> str:

        lines: List[str] = []
        lines.append(f"Quick fat loss workout ({time_minutes} minutes, {location}, {experience}):")
        lines.append("")

        lines.append("1) Warm-up (5 minutes)")
        lines.append("   - 2 minutes: easy cardio (walk, march in place, bike).")
        lines.append("   - 3 minutes: dynamic mobility - leg swings, arm circles, hip circles.")

        work_block_time = max(10, min(time_minutes - 10, 20))

        lines.append("")
        lines.append(f"2) Main block (~{work_block_time} minutes)")

        if location == "gym":
            lines.append(
                "   Perform this as a circuit (3-4 rounds):\n"
                "   - Goblet squat: 12 reps @ 3-0-1-0 (slow down, strong up)\n"
                "   - Push-up or machine press: 10-12 reps @ 3-0-1-0\n"
                "   - Seated row or cable row: 12 reps @ 2-1-2-0\n"
                "   - Romanian deadlift (DB or bar): 10-12 reps @ 3-1-1-0\n"
                "   Rest 60-75s between rounds. Aim for RPE 7-8."
            )
        else:
            lines.append(
                "   Perform this as a circuit (3-5 rounds):\n"
                "   - Squat or chair squat: 15 reps @ 3-0-1-0\n"
                "   - Incline push-up on table/counter: 10-12 reps @ 3-0-1-0\n"
                "   - Hip hinge with backpack or band: 12 reps @ 3-1-1-0\n"
                "   - Glute bridge: 15 reps @ 2-1-1-0\n"
                "   Rest 45-60s between rounds. Keep breathing controlled."
            )

        if time_minutes >= 20:
            lines.append("")
            lines.append("3) Finisher (3-5 minutes)")
            lines.append(
                "   Choose ONE low-impact option:\n"
                "   - Fast walk or step-ups: 20s fast / 40s easy x 4-6 rounds\n"
                "   - Low step burpee without jump: 6-8 reps on the minute for 4-5 minutes (only if joints feel good)."
            )

        lines.append("")
        lines.append("4) Cool-down (3-5 minutes)")
        lines.append("   - Walk slowly until breathing normalizes.")
        lines.append("   - Gentle stretching for hips, hamstrings, and chest (20-30s each).")

        lines.append("")
        lines.append("General guidance:")
        lines.append("- You should finish feeling challenged but not destroyed.")
        lines.append("- If you cannot speak in full sentences, you are going too hard.")
        lines.append("- 3-5 of these sessions per week is a strong fat loss base when combined with nutrition and sleep.")

        return "\n".join(lines)

    # -------------- INTERNAL: Injury adaptation helper --------------

    def _adapt_strength_for_injury(
        self,
        exercises: List[ExercisePrescription],
        region: str,
    ) -> List[ExercisePrescription]:
        """
        Takes the base strength_exercises and returns an adapted list
        based on injury region using InjuryAdaptationEngine.
        """

        if not region:
            return exercises

        original = exercises
        names = [ex.name for ex in original]

        adapted_names = self.injury_adapter.modify_exercise_list(names, region)

        adapted_strength: List[ExercisePrescription] = []

        # Keep any original prescriptions whose names are still allowed
        for name in adapted_names:
            match = next((ex for ex in original if ex.name == name), None)
            if match:
                adapted_strength.append(match)
            else:
                # New replacement exercise name -> generic prescription
                adapted_strength.append(
                    ExercisePrescription(
                        name=name,
                        sets=3,
                        reps="10-12",
                        tempo="controlled",
                        rest_seconds=60,
                        notes="Selected as a joint-friendly alternative.",
                    )
                )

        return adapted_strength


# ---------------------------------------------------------------------------
# Nutrition & Sleep helpers
# ---------------------------------------------------------------------------

class NutritionGuidance:
    """Simple nutrition guidance based on profile and goal."""

    def generate(self, profile: Dict[str, Any]) -> str:
        age = profile.get("age") or 30
        weight = profile.get("weight_kg") or 70
        height = profile.get("height_cm") or 170
        gender = profile.get("gender") or "other"
        goal = profile.get("goal") or "general health"
        experience = profile.get("experience") or "beginner"

        bmr = HealthCalculator.estimate_bmr(weight, height, age, gender)
        tdee = HealthCalculator.estimate_tdee(bmr, experience)
        target = HealthCalculator.get_calorie_target(tdee, goal)

        return (
            f"Based on your stats, an estimated daily calorie target for **{goal}** is around **{target} kcal**.\n"
            f"- This is based on BMR ~{bmr:.0f} kcal and TDEE ~{tdee} kcal.\n"
            "- For fat loss: focus on protein, fiber, and minimally processed foods.\n"
            "- For muscle gain: ensure enough total calories and 1.6–2.2 g protein/kg bodyweight.\n"
        )


class SleepGuidance:
    """Baseline sleep and recovery guidance."""

    def generate(self, profile: Dict[str, Any]) -> str:
        age = profile.get("age") or 30
        goal = profile.get("goal") or "general health"

        lines: List[str] = []
        lines.append("Sleep & Recovery Recommendations")
        lines.append("--------------------------------")
        lines.append("- Aim for 7–9 hours of quality sleep per night.")
        lines.append("- Keep a consistent sleep and wake time, even on weekends.")
        lines.append("- Make your room dark, cool, and quiet.")
        lines.append("- Avoid heavy meals and screens in the 1–2 hours before bed.")

        if age < 25:
            lines.append("- As a younger adult, your sleep need may be closer to 8–9 hours.")
        if "fat loss" in goal:
            lines.append("- Poor sleep makes fat loss harder; prioritizing sleep improves hunger and energy control.")
        if ("muscle" in goal) or ("strength" in goal):
            lines.append("- Muscle recovery and strength gains happen at rest — sleep is non-negotiable.")

        return "\n".join(lines)
