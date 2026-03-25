"""
Custom exceptions for the Health & Fitness Chatbot
"""


class ChatbotException(Exception):
    """Base exception for all chatbot errors"""
    pass


class MedicalReferralRequired(ChatbotException):
    """Raised when user needs medical consultation before training"""
    
    def __init__(self, message: str, severity: str = "high"):
        self.message = message
        self.severity = severity
        super().__init__(self.message)


class InvalidProfileData(ChatbotException):
    """Raised when profile data is invalid or missing critical fields"""
    pass


class PlanGenerationError(ChatbotException):
    """Raised when workout plan cannot be generated"""
    pass


class NLUParseError(ChatbotException):
    """Raised when natural language understanding fails"""
    pass


class MemoryStoreError(ChatbotException):
    """Raised when profile storage/retrieval fails"""
    pass
