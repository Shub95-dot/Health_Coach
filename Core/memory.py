# %%
import os
import json
from dataclasses import asdict
from datetime import datetime
from typing import Dict, Any

from schemas import UserProfile, SessionState, InjuryStatus


class MemoryStore:
    """
    File-based storage for:
    - UserProfile (permanent user info, goals, injuries…)
    - SessionState (current dialog flow / pending params)
    """

    def __init__(self, base_path: str = "user_data"):
        self.base_path = base_path
        self.profiles_dir = os.path.join(base_path, "profiles")
        self.sessions_dir = os.path.join(base_path, "sessions")

        os.makedirs(self.profiles_dir, exist_ok=True)
        os.makedirs(self.sessions_dir, exist_ok=True)

    # ---------- internal helpers ----------

    def _profile_path(self, user_id: str) -> str:
        return os.path.join(self.profiles_dir, f"{user_id}.json")

    def _session_path(self, user_id: str) -> str:
        return os.path.join(self.sessions_dir, f"{user_id}.json")

    # ---------- PROFILE METHODS ----------

    def load_profile(self, user_id: str) -> UserProfile:
        """
        Load a user's profile from disk.
        If it doesn't exist, return a fresh UserProfile.
        """
        path = self._profile_path(user_id)
        if not os.path.exists(path):
            return UserProfile(user_id=user_id)

        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Reconstruct InjuryStatus if present as dict
        injury_status_data = data.get("injury_status")
        if isinstance(injury_status_data, dict):
            try:
                data["injury_status"] = InjuryStatus(**injury_status_data)
            except TypeError:
                # If structure changed or is invalid, drop it
                data["injury_status"] = None

        return UserProfile(**data)

    def save_profile(self, profile: UserProfile) -> None:
        """
        Save a UserProfile to disk as JSON.
        """
        profile.last_updated = datetime.utcnow().isoformat()
        path = self._profile_path(profile.user_id)

        # asdict will also turn InjuryStatus into a dict
        data = asdict(profile)

        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def merge_parsed_into_profile(self, profile: UserProfile, parsed: Dict[str, Any]) -> UserProfile:
        """
        Merge parsed fields (from NLU or ProfileParser) into the profile.
        Known fields go to top-level attributes; unknown go into extras.
        """
        if not parsed:
            return profile

        known_fields = {
            "name",
            "age",
            "sex",
            "height_cm",
            "weight_kg",
            "goal",
            "duration_weeks",
            "location",
            "time_minutes",
            "experience",
            "injury",
            "pregnant",
            "cycle_phase",
            "equipment",
            "injury_region",
            "injury_severity",
        }

        # Update known attributes
        for key in known_fields:
            if key in parsed and parsed[key] is not None:
                setattr(profile, key, parsed[key])

        # Anything else -> extras if it's not already a real attribute
        for key, value in parsed.items():
            if value is None:
                continue
            if not hasattr(profile, key):
                profile.extras[key] = value

        return profile

    # ---------- SESSION METHODS ----------

    def load_session(self, user_id: str) -> SessionState:
        """
        Load a user's current SessionState.
        If not found, return a fresh one.
        """
        path = self._session_path(user_id)
        if not os.path.exists(path):
            return SessionState()

        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        # SessionState only has simple fields: current_flow, feature_params
        return SessionState(**data)

    def save_session(self, user_id: str, session: SessionState) -> None:
        """
        Persist SessionState to disk.
        """
        path = self._session_path(user_id)
        data = asdict(session)

        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)



