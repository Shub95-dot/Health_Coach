# %%
import json
import os
from dataclasses import dataclass, asdict, field
from datetime import datetime
from typing import Optional, Dict, Any

PROFILES_DIR = "profiles"

class UserProfile:
    user_id: str
    name: Optional[str] = None
    age: Optional[int] = None
    sex: Optional[str] = None
    height_cm: Optional[float] = None
    weight_kg: Optional[float] = None
    goal: Optional[str] = None
    duration_weeks: Optional[int] = None
    location: Optional[str] = None
    time_minutes: Optional[str] = None
    experience: Optional[str] = None
    injury: Optional[str] = None
    pregnant: Optional[bool] = None
    cycle_phase: Optional[str] = None
    equipment: Optional[str] = None
    last_updated: Optional[str] = None

    extras: Dict[str, Any] = field(default_factory=dict)

class MemoryStore:
    
    def __init__(self, base_dir: str = PROFILES_DIR):
        self.base_dir = base_dir
        os.makedirs(self.base_dir, exist_ok=True)

    def _profile_path(self, user_id: str) -> str:
        return os.path.join(self.base_dir, f"{user_id}.json")
    
    def load_profile(self, user_id: str) -> UserProfile:
        path = self._profile_path(user_id)
        if not os.path.exists(path):
            return UserProfile(user_id-user_id)
        
        with open(path, "r", encoding='utf-8') as f:
            data = json.load(f)
        
        return UserProfile(**data)
    
    def save_profile(self, profile: UserProfile) -> None:
        profile.last_updated = datetime.utcnow().isoformat()
        path = self._profile_path(profile.user_id)
        with open(path , "w", encoding = "utf-8") as f:
            json.dump(asdict(profile), f , ensure_ascii= False, indent= 2)
    
    def merge_parsed_into_profile(self, profile: UserProfile, parsed: Dict[str, Any]) ->UserProfile:

        if not parsed:
            return profile
        for key in ["name","age","sex","height_cm","weight_kg",
                    "goal","duration_weeks","location","time_minutes",
                    "experience","injury","pregnant","cycle_phase","equipment"
                    ]:
            if key in parsed and parsed[key] is not None:
                setattr(profile, key, parsed[key])

        for key, value in parsed.items():
            if value is None:
                continue
            if not hasattr(profile, key):
                profile.extras[key] = value
        return profile



