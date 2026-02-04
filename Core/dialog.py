# %%
from typing import List

from schemas import (
    UserProfile,
    SessionState,
    GoalParams,
    NLUResult,
)
from injury_engine import InjuryEngine
from workout_engine import PlanGenerator
from exceptions import MedicalReferralRequired


class DialogManager:
    """
    Orchestrates high-level dialog:
    - Reads NLUResult (intent + slots + safety flags)
    - Updates SessionState + UserProfile
    - Calls PlanGenerator to build programs
    - Integrates InjuryEngine to set injury region + severity
    """

    REQUIRED_PLAN_FIELDS = [
        "goal",
        "duration_weeks",
        "experience",
        "location",
        "time_minutes",
    ]

    def __init__(self) -> None:
        self.planner = PlanGenerator()
        self.injury_engine = InjuryEngine()

    # ================= MAIN ENTRY =================

    def handle(
        self,
        nlu_result: NLUResult,
        profile: UserProfile,
        session: SessionState,
    ) -> str:
        """
        Main routing function.
        """

        # ===== SAFETY FIRST (from NLU flags) =====
        if nlu_result.safety_flags:
            # We don't need to be fancy here; orchestrator will catch this
            raise MedicalReferralRequired(
                f"Safety flags detected: {', '.join(nlu_result.safety_flags)}"
            )

        # ===== INJURY CLASSIFICATION (if injury mentioned) =====
        injury_status = None
        if "injury" in nlu_result.slots:
            injury_text = nlu_result.slots["injury"]
            injury_status = self.injury_engine.classify(injury_text)

            # Persist in profile
            profile.injury_status = injury_status
            profile.injury_region = injury_status.region
            profile.injury_severity = injury_status.severity

            # HARD STOP for red injuries
            if injury_status.severity == "red":
                raise MedicalReferralRequired(
                    "This may be a serious injury. Please consult a medical professional before training."
                )

        # ===== MERGE SLOTS INTO SESSION =====
        for k, v in nlu_result.slots.items():
            session.feature_params[k] = v

        intent = nlu_result.intent or "unknown"

        # ===== ROUTING BY INTENT =====
        if intent == "multi_week_plan":
            return self._handle_multi_week_plan(profile, session)

        if intent == "injury_assistance":
            return self._handle_injury()

        if intent == "pregnancy_modification":
            return self._handle_pregnancy()

        if intent == "cycle_modification":
            return self._handle_cycle()

        # Fallback / small talk
        return self._handle_small_talk()

    # ================= PLAN FLOW =================

    def _handle_multi_week_plan(
        self,
        profile: UserProfile,
        session: SessionState,
    ) -> str:
        """
        Build or continue the multi-week plan flow.
        """

        missing = self._missing_fields(session)

        # Still missing required info → ask for next one
        if missing:
            session.current_flow = "multi_week_plan"
            next_field = missing[0]
            return self._ask_for(next_field)

        # All required fields present → assemble params object
        params = GoalParams(
            goal=session.feature_params["goal"],
            duration_weeks=int(session.feature_params["duration_weeks"]),
            experience=session.feature_params["experience"],
            location=session.feature_params["location"],
            time_minutes=int(session.feature_params["time_minutes"]),
        )

        # Save into profile memory
        profile.goal = params.goal
        profile.duration_weeks = params.duration_weeks
        profile.experience = params.experience
        profile.location = params.location
        profile.time_minutes = params.time_minutes

        # Call planner
        plan_text = self.planner.generate_multiweek_plan(
            profile=profile,
            params=params.__dict__,  # planner expects dict
        )

        # Reset session AFTER generating plan
        session.current_flow = None
        session.feature_params.clear()

        return plan_text

    # ================= SPECIAL FLOWS =================

    def _handle_injury(self) -> str:
        return (
            "I can help you train safely around injuries.\n"
            "Tell me:\n"
            "- Which body part is injured?\n"
            "- Pain level (1–10)?\n"
            "- Was it diagnosed by a doctor, and what was the diagnosis?"
        )

    def _handle_pregnancy(self) -> str:
        return (
            "Pregnancy training must be conservative and medically safe.\n"
            "Tell me:\n"
            "- How many weeks pregnant are you?\n"
            "- Any medical restrictions your doctor gave you?\n"
            "- Any symptoms that worry you (bleeding, dizziness, etc.)?"
        )

    def _handle_cycle(self) -> str:
        return (
            "Cycle-aware training can help you feel and perform better.\n"
            "Tell me:\n"
            "- Your current phase (menstrual, follicular, ovulatory, luteal), if you know it.\n"
            "- Rough cycle day (e.g. day 3 of bleeding, day 14, etc.)."
        )

    # ================= UTILITIES =================

    def _missing_fields(self, session: SessionState) -> List[str]:
        """
        Return list of required fields that are still missing
        from the session.feature_params dict.
        """
        return [
            f
            for f in self.REQUIRED_PLAN_FIELDS
            if f not in session.feature_params or session.feature_params[f] in (None, "")
        ]

    def _ask_for(self, field: str) -> str:
        """
        Human-friendly questions for each missing parameter.
        """
        questions = {
            "goal": "What is your main goal? (fat loss / muscle gain / maintenance / general health)",
            "duration_weeks": "How many weeks do you want the plan to last?",
            "experience": "What is your experience level? (beginner / intermediate / advanced)",
            "location": "Where will you train most often? (home / gym)",
            "time_minutes": "How many minutes per session do you realistically have?",
        }

        return questions.get(field, "Tell me more about your training needs.")

    def _handle_small_talk(self) -> str:
        return (
            "I can build multi-week workout plans, quick sessions, or help you adapt training for injury, "
            "pregnancy, or your menstrual cycle.\n"
            "For example, you can say:\n"
            "- \"I want a 6-week fat loss plan at home, beginner, 45 minutes.\"\n"
            "- \"Give me a 20-minute fat loss workout at home.\"\n"
            "- \"I have knee pain, help me train around it.\""
        )


# %%


# %%



