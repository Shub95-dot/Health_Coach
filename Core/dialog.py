import re
from typing import List
from injury_engine import InjuryEngine
from schemas import UserProfile, SessionState, GoalParams, NLUResult
from exceptions import MedicalReferralRequired
from workout_engine import PlanGenerator, NutritionGuidance, HealthCalculator


class DialogManager:

    REQUIRED_ONBOARDING_FIELDS = ["name", "age", "sex", "height_cm", "weight_kg"]
    REQUIRED_PLAN_FIELDS = [
        "goal",
        "duration_weeks",
        "experience",
        "location",
        "time_minutes",
    ]

    def __init__(self):
        self.planner = PlanGenerator()
        self.injury_engine = InjuryEngine()
        self.nutrition_guidance = NutritionGuidance()

    def handle(self, nlu_result: NLUResult, profile: UserProfile, session: SessionState) -> str:
        # ===== SAFETY FIRST (from NLU) =====
        if nlu_result.safety_flags:
            raise MedicalReferralRequired(
                f"Safety flags detected: {', '.join(nlu_result.safety_flags)}"
            )

        # ===== MERGE SLOTS INTO PROFILE/SESSION =====
        for k, v in nlu_result.slots.items():
            if k in self.REQUIRED_ONBOARDING_FIELDS:
                setattr(profile, k, v)
            else:
                session.feature_params[k] = v

        # ===== INJURY CLASSIFICATION =====
        if "injury" in nlu_result.slots:
            injury_text = nlu_result.slots["injury"]
            injury_status = self.injury_engine.classify(injury_text)
            profile.injury_status = injury_status
            profile.injury_region = injury_status.region
            profile.injury_severity = injury_status.severity

            if injury_status.severity == "red":
                raise MedicalReferralRequired(
                    "This may be a serious injury. Please consult a medical professional."
                )

        # ===== ORIENTATION / ONBOARDING =====
        missing_onboarding = self._missing_onboarding(profile)
        
        # Robustness: Check if we just asked for something and the user answered directly
        if session.current_flow == "onboarding":
            last_asked = session.feature_params.get("_last_asked_onboarding")
            # If the user didn't provide the slot we specifically asked for
            if last_asked in self.REQUIRED_ONBOARDING_FIELDS and last_asked not in nlu_result.slots:
                val = nlu_result.original_text.strip()
                if val:
                    candidate = None
                    if last_asked == "name":
                        # Cleaning: remove common prefixes, then take the first word
                        clean_val = re.sub(r"(?i)^(my name is|i am|i'm|name is)\s+", "", val)
                        candidate = clean_val.split()[0].capitalize()
                    elif last_asked in ["age", "height_cm", "weight_kg"]:
                        nums = re.findall(r"(\d+(?:\.\d+)?)", val)
                        if nums: candidate = float(nums[0])
                    elif last_asked == "sex":
                        if "fem" in val.lower(): candidate = "female"
                        elif "male" in val.lower(): candidate = "male"
                    
                    if candidate is not None:
                        setattr(profile, last_asked, candidate)
                        # Refresh missing fields
                        missing_onboarding = self._missing_onboarding(profile)
                
        if missing_onboarding:
            session.current_flow = "onboarding"
            field_to_ask = missing_onboarding[0]
            session.feature_params["_last_asked_onboarding"] = field_to_ask
            return self._ask_for_onboarding(field_to_ask)

        # If onboarding just finished
        if session.current_flow == "onboarding":
            session.current_flow = None
            session.feature_params.pop("_last_asked_onboarding", None)
            stats_text = self._get_health_stats_text(profile)
            return f"Thanks {profile.name}! I've updated your profile.\n\n{stats_text}\n\nWhat would you like to do now? (e.g., 'Build me a 6-week fat loss plan')"

        intent = nlu_result.intent
        
        if intent == "unknown" and session.current_flow and nlu_result.slots:
            intent = session.current_flow

        if intent == "multi_week_plan":
            return self._handle_multi_week_plan(profile, session)

        if intent == "quick_session":
            return self._handle_quick_session(profile, session)

        if intent == "injury_assistance":
            return self._handle_injury(profile, session)

        if intent == "pregnancy_modification":
            return self._handle_pregnancy(profile, session)

        if intent == "cycle_modification":
            return self._handle_cycle(profile, session)

        # Unknown / small talk fallback
        return self._handle_small_talk(profile, session)

    def _missing_onboarding(self, profile: UserProfile) -> List[str]:
        return [f for f in self.REQUIRED_ONBOARDING_FIELDS if getattr(profile, f, None) is None]

    def _ask_for_onboarding(self, field: str) -> str:
        prompts = {
            "name": "Hi! Before we start, what's your name?",
            "age": "Nice to meet you! How old are you?",
            "sex": "What is your sex? (male/female)",
            "height_cm": "What is your height in cm? (e.g., 175cm or 5'9)",
            "weight_kg": "What is your weight? (e.g., 80kg or 175lbs)",
        }
        return prompts.get(field, f"Please tell me your {field}.")

    def _get_health_stats_text(self, profile: UserProfile) -> str:
        if not all([profile.weight_kg, profile.height_cm, profile.age, profile.sex]):
            return "_Complete your profile (age, sex, height, weight) to see your health statistics here._"
            
        bmi = HealthCalculator.calculate_bmi(profile.weight_kg, profile.height_cm)
        cat = HealthCalculator.get_bmi_category(bmi)
        bmr = HealthCalculator.estimate_bmr(profile.weight_kg, profile.height_cm, profile.age, profile.sex)
        tdee = HealthCalculator.estimate_tdee(bmr, profile.experience or "beginner")
        
        return (
            f"**Your Health Stats:**\n"
            f"- **BMI:** {bmi:.1f} ({cat})\n"
            f"- **BMR:** {bmr:.0f} kcal/day\n"
            f"- **TDEE:** ~{tdee:.0f} kcal/day (at your current activity level)"
        )

    # ================= PLAN FLOW =================

    def _handle_multi_week_plan(self, profile: UserProfile, session: SessionState) -> str:
        # 1) Check what we still need
        missing = self._missing_fields(session)

        if missing:
            session.current_flow = "multi_week_plan"
            # Loop detection: if we are asking for the same thing again
            current_ask = missing[0]
            if session.last_intent == "multi_week_plan" and session.feature_params.get("_last_asked") == current_ask:
                # User provided something but we didn't get it.
                return f"I didn't quite catch that. {self._ask_for(current_ask, explicit=True)}"
            
            session.feature_params["_last_asked"] = current_ask
            session.last_intent = "multi_week_plan"
            return self._ask_for(current_ask)

        # 2) Build params object from session slots
        raw_goal = session.feature_params.get("goal", "general health")
        raw_duration = session.feature_params.get("duration_weeks", 8)
        raw_experience = session.feature_params.get("experience", "beginner")
        raw_location = session.feature_params.get("location", "home")
        raw_time = session.feature_params.get("time_minutes", 45)

        recommended_weeks = self._normalize_duration_weeks(raw_goal, int(raw_duration))

        params = GoalParams(
            goal=raw_goal,
            duration_weeks=recommended_weeks,
            experience=raw_experience,
            location=raw_location,
            time_minutes=raw_time
        )

        # 4) Save into profile memory
        profile.goal = params.goal
        profile.duration_weeks = params.duration_weeks
        profile.experience = params.experience
        profile.location = params.location
        profile.time_minutes = params.time_minutes

        # 5) Generate plan
        plan_text = self.planner.generate_multiweek_plan(profile, params.__dict__)

        # 6) Reset session
        session.current_flow = None
        session.feature_params.clear()
        session.last_intent = None

        # 7) If we changed the duration, explain it
        if recommended_weeks != int(raw_duration):
            prefix = (
                f"You asked for a **{raw_duration}-week** plan.\n"
                f"For **{params.goal}**, I recommend **{recommended_weeks} weeks**, "
                f"so I’ve built a {recommended_weeks}-week program for you.\n\n"
            )
            return prefix + plan_text

        return plan_text

    def _handle_quick_session(self, profile: UserProfile, session: SessionState) -> str:
        params = {
            "goal": session.feature_params.get("goal") or getattr(profile, "goal", None) or "fat loss",
            "time_minutes": int(session.feature_params.get("time_minutes") or getattr(profile, "time_minutes", 0) or 20),
            "location": session.feature_params.get("location") or getattr(profile, "location", None) or "home",
            "experience": session.feature_params.get("experience") or getattr(profile, "experience", None) or "beginner",
        }
        
        # Persist last used context
        profile.goal = params["goal"]
        profile.time_minutes = params["time_minutes"]
        profile.location = params["location"]
        profile.experience = params["experience"]

        workout_text = self.planner.generate_quick_workout(profile, params)
        # Clear session to allow new requests
        session.feature_params.clear()
        session.current_flow = None
        return workout_text

    # ================= SPECIAL FLOWS =================

    def _handle_injury(self, profile: UserProfile, session: SessionState) -> str:
        region = getattr(profile, "injury_region", None) or "the affected area"
        severity = getattr(profile, "injury_severity", None)
        severity_line = ""
        if severity == "yellow":
            severity_line = "This sounds like a yellow-flag issue – we’ll be conservative.\n"
        elif severity == "green":
            severity_line = "This looks like a lower-risk issue, but we'll still stay joint-friendly.\n"

        return (
            f"I’ve noted you have an issue around {region}.\n"
            f"{severity_line}"
            "To adapt your training, tell me:\n"
            "- How long has this been going on?\n"
            "- Which movements make it worse?\n"
            "- What can you do right now?\n\n"
            "Once you're ready, say: “Build me a 6-week plan for fat loss at home, beginner, 45 minutes, and adapt it.”"
        )

    def _handle_pregnancy(self, profile: UserProfile, session: SessionState) -> str:
        return (
            "Noted – we’ll keep everything conservative for your pregnancy.\n"
            "Please tell me your weeks, any restrictions, and your prior exercise level.\n"
            "Then you can ask for a plan (e.g. '6-week home plan')."
        )

    def _handle_cycle(self, profile: UserProfile, session: SessionState) -> str:
        return (
            "Cycle-aware training ready.\n"
            "Please tell me your current phase (menstrual, follicular, ovulatory, luteal) and how you feel.\n"
            "Example: 'I'm in luteal phase, feeling low energy. Adjust my plan.'"
        )

    # ================= UTILITIES =================

    def _missing_fields(self, session: SessionState) -> List[str]:
        return [f for f in self.REQUIRED_PLAN_FIELDS if f not in session.feature_params]

    def _ask_for(self, field: str, explicit: bool = False) -> str:
        questions = {
            "goal": "What is your main goal? (fat loss, muscle gain, endurance, general health)",
            "duration_weeks": "How many weeks do you want this plan to last? (e.g. 4, 8, 12)",
            "experience": "What is your experience level? (beginner, intermediate, advanced)",
            "location": "Where will you train? (home or gym)",
            "time_minutes": "How many minutes per session? (e.g. 30, 45, 60)",
        }
        
        q = questions.get(field, "Tell me more about your training preferences (goal, weeks, location, time).")
        if explicit:
            return f"Please try to be specific. {q}"
        return q

    def _normalize_duration_weeks(self, goal: str, requested_weeks: int) -> int:
        g = (goal or "").lower().strip()
        if "fat" in g or "loss" in g or "cut" in g or "recomp" in g:
            if requested_weeks <= 3: return 4
            elif requested_weeks <= 5: return 6
            elif requested_weeks <= 7: return 8
            elif requested_weeks <= 10: return 10
            else: return 12
        if "muscle" in g or "hypertrophy" in g:
            if requested_weeks <= 4: return 8
            elif requested_weeks <= 10: return 12
            else: return 16
        if requested_weeks <= 3: return 4
        elif requested_weeks <= 6: return 6
        elif requested_weeks <= 8: return 8
        else: return 12

    def _handle_small_talk(self, profile: UserProfile, session: SessionState) -> str:
        return (
            "Hi! I’m your coach. I can build multi-week plans or quick workouts.\n"
            "To start, tell me your goal, weeks, location, and experience.\n"
            "Example: '8-week fat loss plan, beginner, home, 45 mins.'"
        )
