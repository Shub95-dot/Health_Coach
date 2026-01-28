import json
import os
from typing import Optional, Dict
from dataclasses import asdict, is_dataclass

from app.Core.schemas import UserProfile, SessionState


class MemoryStore:

    def __init__(self, base_path: str = "user_data"):
        self.base_path = base_path
        os.makedirs(self.base_path, exist_ok=True)

    # -------- PROFILE STORAGE --------

    def _profile_path(self, user_id: str) -> str:
        return os.path.join(self.base_path, f"{user_id}_profile.json")

    def load_profile(self, user_id: str) -> UserProfile:
        path = self._profile_path(user_id)
        if not os.path.exists(path):
            return UserProfile(user_id=user_id)  # new blank profile

        with open(path, "r") as f:
            data = json.load(f)
            return UserProfile(**data)

    def save_profile(self, profile: UserProfile):
        if not is_dataclass(profile):
            raise ValueError("Profile must be a dataclass instance")

        path = self._profile_path(profile.user_id)
        with open(path, "w") as f:
            json.dump(asdict(profile), f, indent=2)

    # -------- SESSION STORAGE --------

    def _session_path(self, user_id: str) -> str:
        return os.path.join(self.base_path, f"{user_id}_session.json")

    def load_session(self, user_id: str) -> SessionState:
        path = self._session_path(user_id)
        if not os.path.exists(path):
            return SessionState()

        with open(path, "r") as f:
            data = json.load(f)
            return SessionState(**data)

    def save_session(self, user_id: str, session: SessionState):
        path = self._session_path(user_id)
        with open(path, "w") as f:
            json.dump(asdict(session), f, indent=2)

    # -------- CLEAR (OPTIONAL) --------

    def clear_session(self, user_id: str):
        path = self._session_path(user_id)
        if os.path.exists(path):
            os.remove(path)
