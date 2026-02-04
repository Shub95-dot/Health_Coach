import os
import json
from dataclasses import asdict
from datetime import datetime
from typing import Dict, Any

from schemas import UserProfile, SessionState  # InjuryStatus not needed here


class MemoryStore:
    def __init__(self, base_path: str = "user_data"):
        self.base_path = base_path
        self.profiles_dir = os.path.join(base_path, "profiles")
        self.sessions_dir = os.path.join(base_path, "sessions")
        os.makedirs(self.profiles_dir, exist_ok=True)
        os.makedirs(self.sessions_dir, exist_ok=True)

    def _profile_path(self, user_id: str) -> str:
        return os.path.join(self.profiles_dir, f"{user_id}.json")

    def _session_path(self, user_id: str) -> str:
        return os.path.join(self.sessions_dir, f"{user_id}.json")

    # ---------- PROFILE ----------

    def load_profile(self, user_id: str) -> UserProfile:
        path = self._profile_path(user_id)
        if not os.path.exists(path):
            # New user → empty profile with this ID
            return UserProfile(user_id=user_id)

        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Backward-compat: inject user_id if missing
        if "user_id" not in data:
            data["user_id"] = user_id

        return UserProfile(**data)

    def save_profile(self, profile: UserProfile) -> None:
        profile.last_updated = datetime.utcnow().isoformat()
        path = self._profile_path(profile.user_id)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(asdict(profile), f, ensure_ascii=False, indent=2)

    # ---------- SESSION ----------

    def load_session(self, user_id: str) -> SessionState:
        path = self._session_path(user_id)
        if not os.path.exists(path):
            # First time we see this user → fresh session
            return SessionState(
                user_id=user_id,
                current_flow=None,
                feature_params={}
            )

        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Backward-compat for old session files
        if "user_id" not in data:
            data["user_id"] = user_id
        if "current_flow" not in data:
            data["current_flow"] = None
        if "feature_params" not in data:
            data["feature_params"] = {}

        return SessionState(**data)

    def save_session(self, user_id: str, session: SessionState) -> None:
        path = self._session_path(user_id)
        payload = asdict(session)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)

    # ---------- MERGING PARSED DATA ----------

    def merge_parsed_into_profile(self, profile: UserProfile, parsed: Dict[str, Any]) -> UserProfile:
        if not parsed:
            return profile

        # Known fields
        for key in [
            "name", "age", "sex", "height_cm", "weight_kg",
            "goal", "duration_weeks", "location", "time_minutes",
            "experience", "injury", "pregnant", "cycle_phase", "equipment"
        ]:
            if key in parsed and parsed[key] is not None:
                setattr(profile, key, parsed[key])

        # Any unknown fields → extras dict
        for key, value in parsed.items():
            if value is None:
                continue
            if not hasattr(profile, key):
                profile.extras[key] = value

        return profile
