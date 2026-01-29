from typing import List

from app.Core.schemas import (
    UserProfile,
    SessionState,
    GoalParams,
    NLUResult
)

from app.Core.exceptions import (
    MedicalReferralRequired
)

from app.Core.workout_engine import PlanGenerator


class DialogManager:

    REQUIRED_PLAN_FIELDS = [
        "goal",
        "duration_weeks",
        "experience",
        "location",
        "time_minutes"
    ]

    def __init__(self):
        self.planner = PlanGenerator()

    # ================= MAIN ENTRY =================

    def handle(self, nlu_result: NLUResult, profile: UserProfile, session: SessionState) -> str:

        # ===== SAFETY FIRST =====
        if nlu_result.safety_flags:
            raise MedicalReferralRequired(
                f"Safety flags detected: {', '.join(nlu_result.safety_flags)}"
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

        return self._handle_small_talk()

    # ================= PLAN FLOW =================

    def _handle_multi_week_plan(self, profile: UserProfile, session: SessionState) -> str:

        missing = self._missing_fields(session)

        if missing:
            session.current_flow = "multi_week_plan"
            return self._ask_for(missing[0])

        params = GoalParams(
            goal=session.feature_params["goal"],
            duration_weeks=session.feature_params["duration_weeks"],
            experience=session.feature_params["experience"],
            location=session.feature_params["location"],
            time_minutes=session.feature_params["time_minutes"]
        )

        # Save into profile memory
        profile.goal = params.goal
        profile.duration_weeks = params.duration_weeks
        profile.experience = params.experience
        profile.location = params.location
        profile.time_minutes = params.time_minutes

        plan_text = self.planner.generate_multiweek_plan(profile, params.__dict__)

        # Reset session
        session.current_flow = None
        session.feature_params.clear()

        return plan_text

    # ================= SPECIAL FLOWS =================

    def _handle_injury(self):
        return (
            "I can help you train safely around injuries.\n"
            "Tell me:\n"
            "- Which body part is injured?\n"
            "- Pain level (1–10)?\n"
            "- Was it diagnosed?"
        )

    def _handle_pregnancy(self):
        return (
            "Pregnancy training must be conservative.\n"
            "Tell me:\n"
            "- Weeks pregnant?\n"
            "- Any medical restrictions?"
        )

    def _handle_cycle(self):
        return (
            "Cycle-aware training can improve results.\n"
            "Tell me:\n"
            "- Current phase (menstrual, follicular, ovulatory, luteal)?\n"
            "- Cycle day if known?"
        )

    # ================= UTILITIES =================

    def _missing_fields(self, session: SessionState) -> List[str]:
        return [
            f for f in self.REQUIRED_PLAN_FIELDS
            if f not in session.feature_params
        ]

    def _ask_for(self, field: str) -> str:

        questions = {
            "goal": "What is your main goal? (fat loss / muscle gain / maintenance)",
            "duration_weeks": "How many weeks do you want the plan to last?",
            "experience": "Experience level? (beginner / intermediate / advanced)",
            "location": "Where will you train? (home / gym)",
            "time_minutes": "How many minutes per session?"
        }

        return questions.get(field, "Tell me more about your training needs.")

    def _handle_small_talk(self):
        return (
            "I can build workout plans, quick sessions, or help with injury, pregnancy, or cycle-aware training.\n"
            "Tell me your goal."
        )
