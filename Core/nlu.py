import re
import difflib
from typing import Dict, Any, List, Optional
from schemas import NLUResult

class NLU:
    """
    Enhanced rule-based NLU with fuzzy matching and broader patterns.
    """
    def __init__(self) -> None:
        self.goal_map = {
            "fat loss": ["fat loss", "lose fat", "weight loss", "weightloss", "fatloss", "cutting", "cut", "recomp", "recomposition"],
            "muscle gain": ["muscle gain", "musclegain", "build muscle", "hypertrophy", "bulk", "bulking", "muscle"],
            "strength": ["strength", "strong", "powerlifting", "power"],
            "endurance": ["endurance", "cardio", "stamina", "fitness"],
            "flexibility": ["flexibility", "stretching", "yoga", "mobility"],
            "general health": ["general health", "health", "fitness", "healthy"]
        }
        
        self.location_map = {
            "home": ["home", "house", "outside", "park", "hm"],
            "gym": ["gym", "fitness center", "health club", "gim"]
        }
        
        self.experience_map = {
            "beginner": ["beginner", "newbie", "novice", "beg", "start"],
            "intermediate": ["intermediate", "med", "inter", "avg"],
            "advanced": ["advanced", "pro", "adv", "expert"]
        }

        self.quick_terms = ["quick", "short", "20 minute", "20-minute", "15 minute", "15-minute", "express", "fast"]
        self.injury_terms = ["injury", "injured", "pain", "hurt", "torn", "tear", "sprain", "strain", "discomfort", "cannot walk", "can't walk"]
        self.pregnancy_terms = ["pregnant", "pregnancy", "prenatal", "postnatal"]
        self.cycle_terms = ["menstrual", "period", "cycle", "follicular", "ovulatory", "luteal", "pms"]
        
        self.red_flag_terms = ["fracture", "broken", "rupture", "dislocation", "severe pain", "cannot walk", "cannot bear weight"]

    def _fuzzy_match(self, text: str, mapping: Dict[str, List[str]], cutoff=0.7) -> Optional[str]:
        """Find the best canonical key for a given input text using fuzzy matching on variants."""
        words = re.findall(r"\w+", text.lower())
        for key, variants in mapping.items():
            for word in words:
                # Direct check
                if word in variants:
                    return key
                # Fuzzy check
                matches = difflib.get_close_matches(word, variants, n=1, cutoff=cutoff)
                if matches:
                    return key
        return None

    def parse(self, text: str) -> NLUResult:
        text = (text or "").strip()
        lower = text.lower()
        
        intent = self._detect_intent(lower)
        slots = self._extract_slots(lower, original_text=text)
        safety_flags = self._detect_safety_flags(lower)
        
        confidence = 0.9 if intent != "unknown" or slots else 0.4
        return NLUResult(intent=intent, slots=slots, confidence=confidence, safety_flags=safety_flags, original_text=text)

    def _detect_intent(self, text: str) -> str:
        if any(term in text for term in self.injury_terms): return "injury_assistance"
        if any(term in text for term in self.pregnancy_terms): return "pregnancy_modification"
        if any(term in text for term in self.cycle_terms): return "cycle_modification"
        
        if (any(term in text for term in self.quick_terms) or "quick" in text) and any(w in text for w in ["workout", "session", "training"]): 
            return "quick_session"
        
        has_goal = self._fuzzy_match(text, self.goal_map) is not None
        has_stats = any(re.search(p, text) for p in [r"\d+\s*cm", r"\d+\s*kg", r"age:?\s*\d+", r"my name is"])
        
        if has_goal or has_stats:
            return "multi_week_plan"
            
        return "unknown"

    def _extract_slots(self, text: str, original_text: str) -> Dict[str, Any]:
        slots: Dict[str, Any] = {}
        
        # Goal extraction
        goal = self._fuzzy_match(text, self.goal_map)
        if goal: slots["goal"] = goal
        
        # Demographic stats
        m_name = re.search(r"(?i)(?:my name is|i'm|i am)\s+([a-zA-Z]+)", text)
        if m_name: 
            slots["name"] = m_name.group(1).capitalize()
        elif len(text.split()) == 1 and text[0].isupper():
            # If it's just one word and capitalized, assume it's a name
            slots["name"] = text.strip().capitalize()
        
        m_age = re.search(r"(?:i'm|i am|age:?)\s*(\d{1,2})(?:\s*years|yrs|yo)?", text)
        if m_age: slots["age"] = int(m_age.group(1))

        if "male" in text or " man" in text or " boy" in text: slots["sex"] = "male"
        elif "female" in text or " woman" in text or " girl" in text: slots["sex"] = "female"
        
        # Height extraction (cm or feet/inches)
        m_cm = re.search(r"(\d{2,3})\s*cm", text)
        if m_cm: 
            slots["height_cm"] = float(m_cm.group(1))
        else:
            m_ft = re.search(r"(\d)'(\d{1,2})", text)
            if m_ft:
                feet = int(m_ft.group(1))
                inches = int(m_ft.group(2))
                slots["height_cm"] = (feet * 30.48) + (inches * 2.54)
        
        # Weight extraction (kg or lbs)
        m_kg = re.search(r"(\d{2,3})\s*kg", text)
        if m_kg:
            slots["weight_kg"] = float(m_kg.group(1))
        else:
            m_lbs = re.search(r"(\d{2,3})\s*lbs", text)
            if m_lbs:
                slots["weight_kg"] = float(m_lbs.group(1)) * 0.453592
        
        # Duration extraction
        m = re.search(r"(\d+)\s*(?:week|weeks|wk|wks)", text)
        if m: slots["duration_weeks"] = int(m.group(1))
        
        # Experience extraction
        exp = self._fuzzy_match(text, self.experience_map)
        if exp: slots["experience"] = exp
        
        # Location extraction
        loc = self._fuzzy_match(text, self.location_map)
        if loc: slots["location"] = loc
        
        # Time extraction
        m = re.search(r"(\d+)\s*(?:minutes|min|minute|mins)", text)
        if m: slots["time_minutes"] = int(m.group(1))
        
        # Injury region
        injury_pattern = r"(knee|shoulder|back|ankle|wrist|neck|meniscus|acl|rotator cuff|lumbar|disc|tendonitis|tendinitis|sprain|strain|tear|torn|fracture|rupture)"
        if re.search(injury_pattern, text): slots["injury"] = original_text
        
        return slots

    def _detect_safety_flags(self, text: str) -> List[str]:
        if any(term in text for term in self.red_flag_terms): return ["medical"]
        return []
