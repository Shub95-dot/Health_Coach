# %%
from dataclasses import dataclass, field
from typing import Optional, List, Dict


# === USER PROFILE ===
@dataclass
class UserProfile:
    user_id: str
    name: Optional[str] = None
    age: Optional[int] = None
    sex: Optional[str] = None  # "male", "female", "other"

    goal: Optional[str] = None           # "fat loss", "muscle gain", etc.
    experience: Optional[str] = None     # "beginner", "intermediate", "advanced"
    location: Optional[str] = None       # "home" or "gym"
    time_minutes: Optional[int] = None
    duration_weeks: Optional[int] = None

    # Health / constraints
    cycle: Optional['CycleInfo'] = None
    pregnancy: Optional['PregnancyInfo'] = None
    injuries: List['InjuryInfo'] = field(default_factory=list)

    # Future extension hook
    preferences: Dict[str, str] = field(default_factory=dict)


# === SESSION STATE ===
@dataclass
class SessionState:
    current_flow: Optional[str] = None    # e.g., "multi_week_plan", "quick_workout"
    feature_params: Dict[str, any] = field(default_factory=dict)
    awaiting_confirmation: bool = False


# === GOAL PARAMETERS ===
@dataclass
class GoalParams:
    goal: str
    duration_weeks: int
    experience: str
    location: str
    time_minutes: int


# === MENSTRUAL CYCLE INFO ===
@dataclass
class CycleInfo:
    phase: Optional[str] = None     # "follicular", "ovulatory", "luteal", "menstrual"
    day_in_cycle: Optional[int] = None
    cycle_length: Optional[int] = None   # e.g., 28 days


# === PREGNANCY INFO ===
@dataclass
class PregnancyInfo:
    trimester: Optional[int] = None   # 1, 2, 3
    weeks_pregnant: Optional[int] = None


# === INJURY INFO ===
@dataclass
class InjuryInfo:
    body_part: Optional[str] = None     # "shoulder", "knee", "ankle", etc.
    severity: Optional[str] = None      # "mild", "moderate", "severe"
    pain_level: Optional[int] = None    # 1-10 subjective
    acute: Optional[bool] = None
    diagnosed: Optional[bool] = None    # e.g., medical diagnosis provided


@dataclass
class NLUResult:
    intent: Optional[str]
    confidence: float
    slots: Dict[str, any] = field(default_factory=dict)
    safety_flags: List[str] = field(default_factory=list)

@dataclass
class InjuryStatus:
    region: Optional[str] = None
    severity: Optional[str] = None  # green / yellow / red
    description: Optional[str] = None


