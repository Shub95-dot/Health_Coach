# %%
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional


# ===== NLU & INJURY STRUCTS =====

@dataclass
class InjuryStatus:
    """
    Structured result from InjuryEngine.classify().
    region: 'knee', 'shoulder', 'back', etc.
    severity: 'green', 'yellow', 'red'
    description: raw user text or a short summary.
    """
    region: str
    severity: str
    description: str = ""


@dataclass
class NLUResult:
    """
    Output of NLU.parse().
    - intent: high-level string, e.g. 'multi_week_plan', 'injury_assistance'
    - slots: extracted fields (goal, weeks, location, time, injury text, etc.)
    - confidence: float, not used heavily yet but could be in future
    - safety_flags: e.g. ['medical'] for red-flag terms
    """
    intent: str
    slots: Dict[str, Any]
    confidence: float
    safety_flags: List[str]


# ===== USER PROFILE & SESSION STATE =====

@dataclass
class UserProfile:
    """
    Long-term per-user state. Saved by MemoryStore.
    This is what the coach 'remembers' about a client.
    """
    user_id: str

    name: Optional[str] = None
    age: Optional[int] = None
    sex: Optional[str] = None

    height_cm: Optional[float] = None
    weight_kg: Optional[float] = None

    goal: Optional[str] = None
    duration_weeks: Optional[int] = None
    location: Optional[str] = None
    time_minutes: Optional[int] = None
    experience: Optional[str] = None

    injury: Optional[str] = None
    pregnant: Optional[bool] = None
    cycle_phase: Optional[str] = None
    equipment: Optional[str] = None

    # Injury-specific structured fields
    injury_region: Optional[str] = None
    injury_severity: Optional[str] = None
    injury_status: Optional[InjuryStatus] = None

    last_updated: Optional[str] = None

    # Catch-all for extra attributes we might add later
    extras: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SessionState:
    """
    Short-term conversational state (per session).
    Not the client's entire history, just the current flow.
    """
    current_flow: Optional[str] = None   # e.g. 'multi_week_plan'
    feature_params: Dict[str, Any] = field(default_factory=dict)


# ===== GOAL PARAMS FOR PLAN GENERATOR =====

@dataclass
class GoalParams:
    """
    Cleaned parameter bundle for passing into PlanGenerator.
    DialogManager will construct this from session.feature_params.
    """
    goal: str
    duration_weeks: int
    experience: str
    location: str
    time_minutes: int



