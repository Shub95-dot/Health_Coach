from typing import List

from injury_engine import InjuryEngine
from schemas import (
    UserProfile,
    SessionState,
    GoalParams,
    NLUResult,
)
from exceptions import MedicalReferralRequired
from workout_engine import PlanGenerator


class DialogManager:
    """
    Orchestrates high-level conversation:
      - Uses NLUResult (intent, slots, safety_flags)
      - Maintains SessionState.current_flow
      - Calls PlanGenerator for multi-week plans
      - Integrates InjuryEngine for injury region + severity
    """

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

    # ================= MAIN ENTRY =================

    def handle(self, nlu_result: NLUResult, profile: UserProfile, session: SessionState) -> str:
        """
        Main routing method called by HealthWellnessChatbot.
        """

        # ===== 1) SAFETY FROM NLU RED FLAGS =====
        if nlu_result.safety_flags:
            raise MedicalReferralRequired(
                f"Safety flags detected in your message ({', '.join(nlu_result.safety_flags)})."
            )

        # ===== 2) INJURY CLASSIFICATION (IF PRESENT) =====
        injury_status = None
        injury_text = nlu_result.slots.get("injury")

        if injury_text:
            injury_status = self.injury_engine.classify(injury_text)

            # Persist on profile
            profile.injury_status = injury_status
            profile.injury_region = injury_status.region
            profile.injury_severity = injury_status.severity

        # Hard stop for "red" injuries detected by InjuryEngine
        if injury_status and injury_status.severity == "red":
            raise MedicalReferralRequired(
                "This may be a serious injury (red-flag). "
                "Please consult a medical professional before continuing training."
            )

        # ===== 3) MERGE SLOTS INTO SESSION FEATURE PARAMS =====
        # (We accumulate info over multiple turns.)
        for k, v in nlu_result.slots.items():
            session.feature_params[k] = v

        intent = nlu_result.intent

        # ===== 4) FLOW OVERRIDE: CONTINUE EXISTING FLOW ON UNKNOWN =====
        # If NLU can't confidently assign a new intent, but we are already in a flow,
        # treat the message as continuation of that flow instead of falling back to small talk.
        if intent == "unknown" and session.current_flow:
            intent = session.current_flow

        # ===== 5) ROUTING BY INTENT =====

        if intent == "multi_week_plan":
            session.current_flow = "multi_week_plan"
            return self._handle_multi_week_plan(profile, session)
        
        if intent == "quick_session":
            session.current_flow = "quick_session"
            return self._handle_quick_session(profile, session)


        if intent == "injury_assistance":
            session.current_flow = "injury_assistance"
            return self._handle_injury(profile, session)

        if intent == "pregnancy_modification":
            session.current_flow = "pregnancy_modification"
            return self._handle_pregnancy(profile, session)

        if intent == "cycle_modification":
            session.current_flow = "cycle_modification"
            return self._handle_cycle(profile, session)

        # Fallback: generic “what do you want help with?”
        session.current_flow = None
        return self._handle_small_talk(profile, session)

    # ================= PLAN FLOW =================

    def _handle_multi_week_plan(self, profile: UserProfile, session: SessionState) -> str:
        """
        Build or continue building a multi-week plan request.
        If required fields are missing, ask a targeted follow-up.
        """
        missing = self._missing_fields(session)

        if missing:
            # Stay in this flow and ask for the next missing parameter
            field = missing[0]
            return self._ask_for(field)

        # All required fields present → construct GoalParams
        params = GoalParams(
            goal=session.feature_params["goal"],
            duration_weeks=int(session.feature_params["duration_weeks"]),
            experience=session.feature_params["experience"],
            location=session.feature_params["location"],
            time_minutes=int(session.feature_params["time_minutes"]),
        )

        # Persist into profile memory
        profile.goal = params.goal
        profile.duration_weeks = params.duration_weeks
        profile.experience = params.experience
        profile.location = params.location
        profile.time_minutes = params.time_minutes

        # If we have injury info on profile, PlanGenerator will adapt around it
        plan_text = self.planner.generate_multiweek_plan(profile, params.__dict__)

        # Reset flow after completing the plan
        session.current_flow = None
        session.feature_params.clear()

        return plan_text
    
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
            "I’m your training coach – I can:\n"
            "- Build multi-week plans (fat loss, muscle gain, endurance, general health)\n"
            "- Give quick workouts for when you’re short on time\n"
            "- Adapt training around injuries, pregnancy, or your cycle\n\n"
            "To get started, tell me something like:\n"
            "- “6-week fat loss plan, beginner, home, 45 minutes.”\n"
            "- “20-minute workout for fat loss at home.”\n"
            "- “I have knee pain and I want to keep training safely.”"
        )
