# %%

class ChatbotError(Exception):
    """Base class for chatbot errors."""


class LowConfidenceIntent(ChatbotError):
    """Thrown when NLU cannot determine intent confidently."""


class MissingParameters(ChatbotError):
    """Thrown when a plan or flow needs more information."""


class UnsupportedGoalException(ChatbotError):
    """Thrown when planner receives an unknown training goal."""


class UnsafeExerciseException(ChatbotError):
    """Thrown when certain exercises are contraindicated."""


class MedicalReferralRequired(ChatbotError):
    """Thrown for red flag symptoms requiring medical review."""









