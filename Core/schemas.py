from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List


# =========================
# INJURY STATUS
# =========================

@dataclass
class InjuryStatus:
    """
    Output of the InjuryEngine.
    region: e.g. 'knee', 'shoulder', 'back', ...
    severity: 'green' | 'yellow' | 'red'
    description: raw text / brief summary of the problem
    """
    region: str
    severity: str      # "green", "yellow", or "red"
    description: str = ""


# =========================
# USER PROFILE (PERSISTED)
# =========================

@dataclass
class UserProfile:
    """
    Long-lived user record.
    Persisted by MemoryStore and updated from parsed free text + slots.
    """
    user_id: str

    # Basic demographics
    name: Optional[str] = None
    age: Optional[int] = None
    sex: Optional[str] = None               # 'male', 'female', 'other'
    height_cm: Optional[float] = None
    weight_kg: Optional[float] = None

    # Training preferences / last request
    goal: Optional[str] = None              # 'fat loss', 'muscle gain', etc.
    duration_weeks: Optional[int] = None
    location: Optional[str] = None          # 'home' or 'gym'
    time_minutes: Optional[int] = None
    experience: Optional[str] = None        # 'beginner' / 'intermediate' / 'advanced'

    # Health & constraints
    injury: Optional[str] = None            # free text from user
    injury_region: Optional[str] = None     # e.g. 'knee'
    injury_severity: Optional[str] = None   # 'green' / 'yellow' / 'red'
    injury_status: Optional[InjuryStatus] = None

    pregnant: Optional[bool] = None
    cycle_phase: Optional[str] = None       # 'menstrual', 'follicular', etc.

    equipment: Optional[str] = None         # free text e.g. 'dumbbells, bench'

    last_updated: Optional[str] = None      # ISO timestamp string

    # Anything we parse but don't have a dedicated field for
    extras: Dict[str, Any] = field(default_factory=dict)


# =========================
# SHORT-LIVED SESSION STATE
# =========================

@dataclass
class SessionState:
    """
    Per-conversation context.
    Not long-term memory: just holds the current flow + collected params.
    """
    user_id: str
    current_flow: Optional[str] = None          # e.g. 'multi_week_plan'
    feature_params: Dict[str, Any] = field(default_factory=dict)
    last_intent: Optional[str] = None
    last_message: Optional[str] = None


# =========================
# GOAL PARAM CONTAINER
# =========================

@dataclass
class GoalParams:
    """
    Canonical parameter bundle passed to the planner.
    Typically built from SessionState.feature_params.
    """
    goal: str
    duration_weeks: int
    experience: str
    location: str
    time_minutes: int


# =========================
# NLU → DIALOG HANDOFF
# =========================

@dataclass
class NLUResult:
    """
    Output of the NLU component.
    Parsed intent, slots, confidence, and any safety flags.
    """
    intent: str
    confidence: float
    slots: Dict[str, Any]
    safety_flags: List[str] = field(default_factory=list)
