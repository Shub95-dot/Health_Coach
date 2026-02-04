from typing import List
from injury_engine import InjuryEngine
from schemas import UserProfile, SessionState, GoalParams, NLUResult
from exceptions import MedicalReferralRequired
from workout_engine import PlanGenerator


class DialogManager:

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

    def handle(self, nlu_result: NLUResult, profile: UserProfile, session: SessionState) -> str:
        # ===== SAFETY FIRST (from NLU) =====
        if nlu_result.safety_flags:
            raise MedicalReferralRequired(
                f"Safety flags detected: {', '.join(nlu_result.safety_flags)}"
            )

        # ===== INJURY CLASSIFICATION =====
        if "injury" in nlu_result.slots:
            injury_text = nlu_result.slots["injury"]
            injury_status = self.injury_engine.classify(injury_text)

            profile.injury_status = injury_status
            profile.injury_region = injury_status.region
            profile.injury_severity = injury_status.severity

            # HARD STOP for red injuries (ONLY if we actually have an injury)
            if injury_status.severity == "red":
                raise MedicalReferralRequired(
                    "This may be a serious injury. Please consult a medical professional before training."
                )

        # ===== MERGE SLOTS INTO SESSION =====
        for k, v in nlu_result.slots.items():
            session.feature_params[k] = v

        intent = nlu_result.intent

        if intent == "multi_week_plan":
            return self._handle_multi_week_plan(profile, session)

        if intent == "injury_assistance":
            return self._handle_injury()

        if intent == "pregnancy_modification":
            return self._handle_pregnancy()

        if intent == "cycle_modification":
            return self._handle_cycle()

        # Unknown / small talk fallback
        return self._handle_small_talk(profile, session)
    
    #Smart Helper#
        
    def _normalize_duration_weeks(self, goal: str, requested_weeks: int) -> int:
        """
        Map arbitrary requested weeks (3, 5, 7, 11, ...) to a sensible
        program length depending on goal.

        This is where you encode "coach logic" instead of rigid enums.
        """

        g = (goal or "").lower().strip()

        # Default ranges per goal – you can tweak these
        if "fat" in g or "loss" in g or "cut" in g or "recomp" in g:
            # Fat loss / recomposition – we like 6–12 weeks
            if requested_weeks <= 3:
                return 4          # minimum meaningful block
            elif requested_weeks <= 5:
                return 6
            elif requested_weeks <= 7:
                return 8
            elif requested_weeks <= 10:
                return 10
            elif requested_weeks <= 12:
                return 12
            else:
                return 12         # cap to 12 for now

        if "muscle" in g or "hypertrophy" in g:
            # Muscle gain takes longer – bias toward 8–16
            if requested_weeks <= 4:
                return 8
            elif requested_weeks <= 7:
                return 8
            elif requested_weeks <= 10:
                return 12
            elif requested_weeks <= 16:
                return 16
            else:
                return 16

        # General health / endurance / flexibility, etc.
        # More forgiving, but still normalised.
        if requested_weeks <= 3:
            return 4
        elif requested_weeks <= 6:
            return 6
        elif requested_weeks <= 8:
            return 8
        elif requested_weeks <= 12:
            return 12
        else:
            return 12



    # ================= PLAN FLOW =================

    def _handle_multi_week_plan(self, profile: UserProfile, session: SessionState) -> str:
        # 1) Check what we still need
        missing = self._missing_fields(session)

        if missing:
            session.current_flow = "multi_week_plan"
            return self._ask_for(missing[0])

        # 2) Build params object from session slots
        raw_goal = session.feature_params.get("goal", "")
        raw_duration = session.feature_params.get("duration_weeks", 8)
        raw_experience = session.feature_params.get("experience", "beginner")
        raw_location = session.feature_params.get("location", "home")
        raw_time = session.feature_params.get("time_minutes", 45)

        try:
            requested_weeks = int(raw_duration)
        except Exception:
            requested_weeks = 8  # fallback

        # 3) Normalise weeks based on goal (THIS is the new logic)
        recommended_weeks = self._normalize_duration_weeks(raw_goal, requested_weeks)

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

        # 7) If we changed the duration, explain it to the user
        if recommended_weeks != requested_weeks:
            prefix = (
                f"You asked for a **{requested_weeks}-week** plan.\n"
                f"For **{params.goal}**, I recommend **{recommended_weeks} weeks**, "
                f"so I’ve built a {recommended_weeks}-week program for you.\n\n"
            )
            return prefix + plan_text

        # If they already asked for a sensible duration, just return the plan
        return plan_text

    def _handle_quick_session(self, profile: UserProfile, session: SessionState) -> str:
        """
        Build a single quick workout based on whatever slots we have.
        This uses PlanGenerator.generate_quick_workout().
        """

        
        params = dict(session.feature_params)

        
        if "goal" not in params and profile.goal:
            params["goal"] = profile.goal

        if "location" not in params and profile.location:
            params["location"] = profile.location

        if "time_minutes" not in params and profile.time_minutes:
            params["time_minutes"] = profile.time_minutes

        if "experience" not in params and profile.experience:
            params["experience"] = profile.experience

      
        params.setdefault("goal", "fat loss")
        params.setdefault("location", "home")
        params.setdefault("time_minutes", 20)
        params.setdefault("experience", "beginner")

        # Call the workout engine
        text = self.planner.generate_quick_workout(profile, params)
        return text

    
    def _handle_quick_session(self, profile: UserProfile, session: SessionState) -> str:
        """
        Build a single quick workout session.
        We use whatever slots we have; missing ones fall back to profile, then defaults.
        """
        # Merge what we know from session + profile
        params = {
            "goal": session.feature_params.get("goal") or getattr(profile, "goal", None) or "fat loss",
            "time_minutes": int(session.feature_params.get("time_minutes") or getattr(profile, "time_minutes", 0) or 20),
            "location": session.feature_params.get("location") or getattr(profile, "location", None) or "home",
            "experience": session.feature_params.get("experience") or getattr(profile, "experience", None) or "beginner",
        }

        # Persist the last used quick-workout context onto profile (optional but useful)
        profile.goal = params["goal"]
        profile.time_minutes = params["time_minutes"]
        profile.location = params["location"]
        profile.experience = params["experience"]

        # Ask PlanGenerator for a quick workout
        workout_text = self.planner.generate_quick_workout(profile, params)

        return workout_text


    # ================= SPECIAL FLOWS =================

    def _handle_injury(self, profile: UserProfile, session: SessionState) -> str:
        """
        Injury assistance entry or continuation.
        We rely on profile.injury_region / injury_severity if available.
        """
        region = getattr(profile, "injury_region", None) or "the affected area"
        severity = getattr(profile, "injury_severity", None)

        severity_line = ""
        if severity == "yellow":
            severity_line = (
                "This sounds like a yellow-flag issue – we’ll be conservative and avoid aggravating movements.\n"
            )
        elif severity == "green":
            severity_line = (
                "This currently looks like a lower-risk (green-flag) issue, but we’ll still keep things joint-friendly.\n"
            )

        return (
            f"I’ve noted you have an issue around {region}.\n"
            f"{severity_line}"
            "To adapt your training properly, tell me:\n"
            "- How long has this been going on?\n"
            "- Which movements or exercises make it worse?\n"
            "- What did your doctor or physio say you *can* do right now?\n\n"
            "Once you answer these, you can say something like:\n"
            "“Now build me a 6-week plan for fat loss at home, beginner, 45 minutes, "
            "and adapt it for my injury.”"
        )

    def _handle_pregnancy(self, profile: UserProfile, session: SessionState) -> str:
        return (
            "Thanks for letting me know about pregnancy – we’ll keep everything conservative.\n"
            "Please tell me:\n"
            "- How many weeks pregnant you are\n"
            "- Any specific medical restrictions you’ve been given\n"
            "- Whether you exercised regularly before pregnancy\n"
        )

    def _handle_cycle(self, profile: UserProfile, session: SessionState) -> str:
        return (
            "Cycle-aware training can absolutely help.\n"
            "Please tell me:\n"
            "- Your current phase (menstrual, follicular, ovulatory, luteal)\n"
            "- Approximate cycle day (if you track it)\n"
            "- Whether you usually feel low-energy or high-energy in this phase\n"
        )

    # ================= UTILITIES =================

    def _missing_fields(self, session: SessionState) -> List[str]:
        return [
            f for f in self.REQUIRED_PLAN_FIELDS
            if f not in session.feature_params
        ]

    def _ask_for(self, field: str) -> str:
        questions = {
            "goal": (
                "What is your main goal right now? "
                "(fat loss, muscle gain, weight gain, endurance, flexibility, general health)"
            ),
            "duration_weeks": "How many weeks do you want this plan to last?",
            "experience": "What is your training experience level? (beginner, intermediate, advanced)",
            "location": "Where will you train most of the time? (home or gym)",
            "time_minutes": "Roughly how many minutes per session do you have? (e.g. 30, 45, 60, 90)",
        }

        return questions.get(
            field,
            "Tell me a bit more about your training preferences (goal, weeks, location, and time per session).",
        )

    def _handle_small_talk(self, profile: UserProfile, session: SessionState) -> str:
        """
        Default fallback when we don't have a clear structured request.
        """
        return (
            "Hi!!\nI’m your training coach – I can:\n"
            "- Build multi-week plans (fat loss, muscle gain, endurance, general health)\n"
            "- Give quick workouts for when you’re short on time\n"
            "- Adapt training around injuries, pregnancy, or your cycle\n\n"
            "To get started, tell me something like:\n"
            "- “6-week fat loss plan, beginner, home, 45 minutes.”\n"
            "- “20-minute workout for fat loss at home.”\n"
            "- “I have knee pain and I want to keep training safely.”"
        )
