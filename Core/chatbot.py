from __future__ import annotations

from typing import Optional, Dict, Any

from nlu import NLU
from memory import MemoryStore
from dialog import DialogManager
from pdf_generator import WorkoutPDFGenerator

from exceptions import (
    ChatbotError,
    MedicalReferralRequired,
    MissingParameters,
    LowConfidenceIntent,
)


class HealthWellnessChatbot:
    """
    Top-level orchestrator.
    """

    def __init__(
        self,
        memory: Optional[MemoryStore] = None,
        nlu: Optional[NLU] = None,
        dialog: Optional[DialogManager] = None,
    ) -> None:
        self.memory = memory or MemoryStore()
        self.nlu = nlu or NLU()
        self.dialog = dialog or DialogManager()
        self.pdf_generator = WorkoutPDFGenerator()

    def process_message(self, user_id: str, message: str) -> Dict[str, Any]:
        """
        Main external API. Returns a dict with 'reply' and optional 'pdf_path'.
        """

        message = (message or "").strip()
        if not message:
            return {
                "reply": "Tell me what you want help with (fat loss, muscle gain, quick workout)."
            }

        # ---- Load state ----
        profile = self.memory.load_profile(user_id)
        session = self.memory.load_session(user_id)

        try:
            # ---- NLU step ----
            nlu_result = self.nlu.parse(message)

            # ---- Dialog / planning step ----
            reply = self.dialog.handle(
                nlu_result=nlu_result,
                profile=profile,
                session=session,
            )

            # ---- Persist updated state ----
            self.memory.save_profile(profile)
            self.memory.save_session(user_id, session)

            # ---- PDF Generation Trigger ----
            # If the reply looks like a plan, generate PDF
            r_lower = reply.lower()
            pdf_path = None
            if ("week" in r_lower and "plan" in r_lower) or ("goal:" in r_lower and "week " in r_lower):
                stats_text = self.dialog._get_health_stats_text(profile)
                pdf_path = self.pdf_generator.generate(
                    user_id=user_id,
                    profile_name=profile.name or "User",
                    stats_text=stats_text,
                    plan_text=reply
                )

            return {"reply": reply, "pdf_path": pdf_path}

        except MedicalReferralRequired:
            self.memory.save_profile(profile)
            self.memory.save_session(user_id, session)
            return {
                "reply": "Based on what you said, I'm not comfortable giving training advice without medical clearance.\nPlease seek medical attention first."
            }
        except Exception as e:
            import traceback
            traceback.print_exc()
            self.memory.save_profile(profile)
            self.memory.save_session(user_id, session)
            return {"reply": f"DEBUG ERROR: {type(e).__name__}: {e}"}

