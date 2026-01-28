import re
from typing import Dict, List
from dataclasses import dataclass, field

from app.Core.schemas import NLUResult


class NLU:

    def __init__(self):
        # === Intent Patterns ===
        self.goal_terms = {
            "fat loss": ["cut", "fat loss", "lose fat", "weight loss", "tone", "shred"],
            "muscle gain": ["bulk", "gain muscle", "build muscle", "hypertrophy"],
            "conditioning": ["conditioning", "endurance", "cardio"],
            "maintenance": ["maintain", "stay fit"]
        }

        self.location_terms = {
            "home": ["home", "living room", "no equipment"],
            "gym": ["gym", "fitness center", "weights", "machines"]
        }

        self.experience_terms = {
            "beginner": ["new", "beginner", "first time"],
            "intermediate": ["intermediate", "experienced"],
            "advanced": ["advanced", "trained", "athlete"]
        }

        # Detection patterns
        self.duration_pattern = re.compile(r"(\d+)\s*(week|weeks|wk|wks)", re.I)
        self.time_pattern = re.compile(r"(\d+)\s*(min|minutes)", re.I)

        self.pregnancy_pattern = re.compile(r"(pregnant|trimester|weeks pregnant)", re.I)
        self.cycle_pattern = re.compile(r"(menstrual|cycle|follicular|luteal|ovulatory)", re.I)
        self.injury_pattern = re.compile(r"(pain|injury|hurt|sprain|strain|tendonitis|fracture)", re.I)

        # Red flag patterns (high severity)
        self.red_flags = [
            "chest pain", "dizziness", "shortness of breath", "bleeding", "fainting"
        ]


    def parse(self, text: str) -> NLUResult:
        text = text.lower()

        slots: Dict[str, any] = {}
        safety_flags: List[str] = []

        # --- Goal Extraction ---
        for goal, terms in self.goal_terms.items():
            if any(t in text for t in terms):
                slots["goal"] = goal

        # --- Location Extraction ---
        for loc, terms in self.location_terms.items():
            if any(t in text for t in terms):
                slots["location"] = loc

        # --- Experience Extraction ---
        for lvl, terms in self.experience_terms.items():
            if any(t in text for t in terms):
                slots["experience"] = lvl

        # --- Duration Extraction ---
        m = self.duration_pattern.search(text)
        if m:
            slots["duration_weeks"] = int(m.group(1))

        # --- Time Extraction ---
        m = self.time_pattern.search(text)
        if m:
            slots["time_minutes"] = int(m.group(1))

        # --- Pregnancy Detection ---
        if self.pregnancy_pattern.search(text):
            slots["pregnancy"] = True

        # --- Cycle Detection ---
        if self.cycle_pattern.search(text):
            slots["cycle"] = True

        # --- Injury Detection ---
        if self.injury_pattern.search(text):
            slots["injury"] = True

        # --- Red Flag Medical Safety ---
        for flag in self.red_flags:
            if flag in text:
                safety_flags.append(flag)

        # Determine intent (basic rule-based for now)
        intent = None
        confidence = 0.6  # baseline

        if "goal" in slots:
            intent = "multi_week_plan"
            confidence = 0.9

        elif "injury" in slots:
            intent = "injury_assistance"
            confidence = 0.8

        elif "pregnancy" in slots:
            intent = "pregnancy_modification"
            confidence = 0.8

        elif "cycle" in slots:
            intent = "cycle_modification"
            confidence = 0.8

        else:
            intent = "small_talk"
            confidence = 0.4

        return NLUResult(
            intent=intent,
            confidence=confidence,
            slots=slots,
            safety_flags=safety_flags
        )
