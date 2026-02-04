# %%
from __future__ import annotations

from typing import Optional

from nlu import NLU
from memory import MemoryStore
from dialog import DialogManager

from exceptions import (
    ChatbotError,
    MedicalReferralRequired,
    MissingParameters,
    LowConfidenceIntent,
)


class HealthWellnessChatbot:
    """
    Top-level orchestrator.

    Responsibilities:
    - Load / save user profile + session via MemoryStore
    - Call NLU.parse(message) to get NLUResult
    - Pass NLUResult + Profile + Session to DialogManager
    - Handle safety / error exceptions and turn them into user-friendly text
    """

    def __init__(
        self,
        memory: Optional[MemoryStore] = None,
        nlu: Optional[NLU] = None,
        dialog: Optional[DialogManager] = None,
    ) -> None:
        # Use provided dependencies if passed in (for future tests),
        # otherwise construct the defaults.
        self.memory = memory or MemoryStore()
        self.nlu = nlu or NLU()
        self.dialog = dialog or DialogManager()

    def process_message(self, user_id: str, message: str) -> str:
        """
        Main external API.

        - user_id: stable id for the user (e.g. "cli_user", auth id, etc.)
        - message: raw user text.
        Returns: reply string to send back to the user.
        """

        message = (message or "").strip()
        if not message:
            return (
                "Tell me what you want help with "
                "(fat loss, muscle gain, quick workout, injury, pregnancy, cycle)."
            )

        # ---- Load state ----
        profile = self.memory.load_profile(user_id)
        # NOTE: we will make sure MemoryStore has load_session/save_session;
        # for now we assume they exist and return a SessionState.
        session = self.memory.load_session(user_id)

        try:
            # ---- NLU step ----
            nlu_result = self.nlu.parse(message)

            # Optional stricter gating in future:
            # if (not nlu_result.intent) or (nlu_result.confidence < 0.45):
            #     raise LowConfidenceIntent("NLU confidence too low")

            # ---- Dialog / planning step ----
            reply = self.dialog.handle(
                nlu_result=nlu_result,
                profile=profile,
                session=session,
            )

            # ---- Persist updated state ----
            self.memory.save_profile(profile)
            self.memory.save_session(user_id, session)

            return reply

        except MedicalReferralRequired:
            # Safety-first; persist state, then give conservative answer.
            self.memory.save_profile(profile)
            self.memory.save_session(user_id, session)
            return (
                "Based on what you said, I'm not comfortable giving training advice "
                "without medical clearance.\n"
                "Please seek medical attention or speak to a qualified clinician first.\n"
                "If you still want help, tell me what a doctor has cleared you to do."
            )

        except MissingParameters:
            # In our current design, DialogManager usually asks follow-up questions
            # itself, but we keep this here as a guard.
            self.memory.save_profile(profile)
            self.memory.save_session(user_id, session)
            return (
                "I need a bit more information to build this safely. "
                "What’s your goal, weeks, location, and time per session?"
            )

        except LowConfidenceIntent:
            self.memory.save_profile(profile)
            self.memory.save_session(user_id, session)
            return (
                "I'm not fully sure what you want yet. Try one of these:\n"
                "- \"I want a 6-week fat loss plan at home, beginner, 45 minutes.\"\n"
                "- \"Give me a 20-minute quick workout for fat loss at home.\"\n"
                "- \"I have knee pain—help me train around it.\""
            )

        except ChatbotError:
            # Controlled “logic” failures in our own code
            self.memory.save_profile(profile)
            self.memory.save_session(user_id, session)
            return (
                "Something went wrong in my coaching logic. "
                "Please rephrase your request with goal, weeks, location, and time per session."
            )

        except Exception:
            # Unknown / unexpected error — don't leak internals
            self.memory.save_profile(profile)
            self.memory.save_session(user_id, session)
            return (
                "I hit an unexpected error. "
                "Try again and include your goal, weeks, location, and time per session."
            )



