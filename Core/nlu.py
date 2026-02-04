import re
from typing import Dict, Any, List
from schemas import NLUResult

class NLU:
    """
    Lightweight, rule-based NLU for:
    - intent classification
    - slot extraction (goal, weeks, location, time, experience, injury)
    - safety flag detection (for medical red flags)
    """
    def __init__(self) -> None:
        self.goal_terms = ["fat loss", "lose fat", "weight loss", "muscle gain", "build muscle", "hypertrophy", "strength", "endurance", "flexibility", "recomposition"]
        self.quick_terms = ["quick", "short", "20 minute", "20-minute", "15 minute", "15-minute", "express"]
        self.injury_terms = ["injury", "injured", "pain", "hurt", "torn", "tear", "sprain", "strain", "discomfort", "cannot walk", "can't walk", "post surgery", "post-surgery"]
        self.pregnancy_terms = ["pregnant", "pregnancy", "prenatal", "postnatal", "post-natal"]
        self.cycle_terms = ["menstrual", "period", "cycle", "follicular", "ovulatory", "luteal", "pms"]

        self.slot_patterns = {
            "goal": r"(fat loss|lose fat|weight loss|muscle gain|build muscle|hypertrophy|strength|endurance|flexibility|recomposition)",
            "duration_weeks": r"(\d+)\s*(?:week|weeks|wk)",
            "experience": r"(beginner|intermediate|advanced)",
            "location": r"\b(home|gym)\b",
            "time_minutes": r"(\d+)\s*(?:minutes|min|minute)",
        }
        self.injury_pattern = r"(knee|shoulder|back|ankle|wrist|neck|meniscus|acl|rotator cuff|lumbar|disc|tendonitis|tendinitis|sprain|strain|tear|torn|fracture|rupture)"
        self.red_flag_terms = ["fracture", "broken", "rupture", "dislocation", "post surgery", "post-surgery", "post op", "post-op", "severe pain", "excruciating", "cannot walk", "can't walk", "cannot bear weight", "can't bear weight"]

    def parse(self, text: str) -> NLUResult:
        text = (text or "").strip()
        lower = text.lower()
        intent = self._detect_intent(lower)
        slots = self._extract_slots(lower, original_text=text)
        safety_flags = self._detect_safety_flags(lower)
        confidence = 0.9 if intent != "unknown" else 0.4
        return NLUResult(intent=intent, slots=slots, confidence=confidence, safety_flags=safety_flags)

    def _detect_intent(self, text: str) -> str:
        if any(term in text for term in self.injury_terms): return "injury_assistance"
        if any(term in text for term in self.pregnancy_terms): return "pregnancy_modification"
        if any(term in text for term in self.cycle_terms): return "cycle_modification"
        if any(term in text for term in self.quick_terms) and ("workout" in text or "session" in text): return "quick_session"
        has_goal = any(term in text for term in self.goal_terms)
        has_weeks = bool(re.search(r"\d+\s*(week|weeks|wk)", text))
        has_plan_words = any(w in text for w in ["plan", "program", "phase", "cycle"])
        if has_goal and (has_weeks or has_plan_words): return "multi_week_plan"
        if has_goal: return "multi_week_plan"
        return "unknown"

    def _extract_slots(self, text: str, original_text: str) -> Dict[str, Any]:
        slots: Dict[str, Any] = {}
        m = re.search(self.slot_patterns["goal"], text)
        if m:
            goal_raw = m.group(1)
            goal_map = {"lose fat": "fat loss", "weight loss": "fat loss", "build muscle": "muscle gain"}
            slots["goal"] = goal_map.get(goal_raw, goal_raw)
        m = re.search(self.slot_patterns["duration_weeks"], text)
        if m: slots["duration_weeks"] = int(m.group(1))
        m = re.search(self.slot_patterns["experience"], text)
        if m: slots["experience"] = m.group(1)
        m = re.search(self.slot_patterns["location"], text)
        if m: slots["location"] = m.group(1)
        m = re.search(self.slot_patterns["time_minutes"], text)
        if m: slots["time_minutes"] = int(m.group(1))
        if re.search(self.injury_pattern, text): slots["injury"] = original_text
        return slots

    def _detect_safety_flags(self, text: str) -> List[str]:
        if any(term in text for term in self.red_flag_terms): return ["medical"]
        return []
