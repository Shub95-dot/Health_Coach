from __future__ import annotations

from typing import Optional

from app.Core.nlu import NLU
from app.Core.memory import MemoryStore
from app.Core.dialog_manager import DialogManager

from app.Core.exceptions import (
    ChatbotError,
    MedicalReferralRequired,
    MissingParameters,
    LowConfidenceIntent,
)


class HealthWellnessChatbot:
    """
    Enterprise orchestrator.
    Connects: NLU -> DialogManager -> Planner (via DialogManager)
    Persists: UserProfile + SessionState via MemoryStore
    """

    def __init__(
        self,
        memory: Optional[MemoryStore] = None,
        nlu: Optional[NLU] = None,
        dialog: Optional[DialogManager] = None,
    ):
        self.memory = memory or MemoryStore(base_path="user_data")
        self.nlu = nlu or NLU()
        self.dialog = dialog or DialogManager()

    def process_message(self, user_id: str, message: str) -> str:
        message = (message or "").strip()
        if not message:
            return "Tell me what you want help with (fat loss, muscle gain, quick workout, injury, pregnancy, cycle)."

        # Load state
        profile = self.memory.load_profile(user_id)
        session = self.memory.load_session(user_id)

        try:
            # NLU
            nlu_result = self.nlu.parse(message)

            # If you want stricter gating, uncomment:
            # if (not nlu_result.intent) or (nlu_result.confidence < 0.45):
            #     raise LowConfidenceIntent("NLU confidence too low")

            # Route + generate reply
            reply = self.dialog.handle(nlu_result=nlu_result, profile=profile, session=session)

            # Persist updated state
            self.memory.save_profile(profile)
            self.memory.save_session(user_id, session)

            return reply

        except MedicalReferralRequired as e:
            # Persist profile/session before responding
            self.memory.save_profile(profile)
            self.memory.save_session(user_id, session)

            # Safety-first message
            return (
                "Based on what you said, I’m not comfortable giving training advice without medical clearance.\n"
                "Please seek medical attention or speak to a qualified clinician first.\n"
                "If you still want help, tell me what a doctor has cleared you to do."
            )

        except MissingParameters as e:
            # Persist and ask follow-up (in our dialog manager we usually ask directly,
            # but keep this boundary for future extensions.)
            self.memory.save_profile(profile)
            self.memory.save_session(user_id, session)
            return "I need a bit more information to build this safely. What’s your goal, weeks, location, and time per session?"

        except LowConfidenceIntent:
            self.memory.save_profile(profile)
            self.memory.save_session(user_id, session)
            return (
                "I’m not fully sure what you want yet. Try one of these:\n"
                "- “I want a 6-week fat loss plan at home, beginner, 45 minutes.”\n"
                "- “Give me a 20-minute quick workout for fat loss at home.”\n"
                "- “I have knee pain—help me train around it.”"
            )

        except ChatbotError:
            # Controlled failures
            self.memory.save_profile(profile)
            self.memory.save_session(user_id, session)
            return "Something went wrong in my coaching logic. Please rephrase your request (goal, weeks, location, time)."

        except Exception:
            # Unknown failures: do not leak internals
            self.memory.save_profile(profile)
            self.memory.save_session(user_id, session)
            return "I hit an unexpected error. Please try again with: goal, weeks, location, and time per session."
