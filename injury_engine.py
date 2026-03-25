"""
Complete Injury Classification Engine
Intelligently classifies injuries and determines safety level
"""

from typing import Dict, List, Optional
from dataclasses import dataclass
import re


@dataclass
class InjuryStatus:
    """Detailed injury status information"""
    region: str = "unspecified"
    severity: str = "green"  # green, yellow, red
    description: str = ""
    pain_level: Optional[int] = None
    diagnosed: bool = False
    injury_type: str = ""  # specific injury name


class InjuryEngine:
    """
    Classifies injuries into red (medical referral), yellow (modify), or green (safe)
    Identifies body region and type of injury
    """
    
    # RED FLAGS - Require immediate medical referral
    RED_FLAG_TERMS = [
        # Structural damage
        "fracture", "broken", "break", "fractured",
        "torn", "tear", "rupture", "ruptured", "ripped",
        "acl tear", "mcl tear", "meniscus tear",
        "rotator cuff tear", "labrum tear",
        
        # Severity indicators
        "severe", "unbearable", "extreme", "excruciating",
        "cannot walk", "can't walk", "unable to walk",
        "cannot move", "can't move", "unable to move",
        "cannot bear weight", "can't bear weight",
        
        # Medical situations
        "post surgery", "post-surgery", "after surgery",
        "post-op", "surgical", "operation",
        "dislocation", "dislocated", "out of socket",
        
        # Neurological
        "numbness", "tingling", "nerve", "shooting pain",
        "radiating", "pins and needles",
        
        # Other serious
        "swelling severe", "huge swelling", "massive swelling",
        "bruising severe", "black and blue",
        "deformity", "deformed", "looks wrong"
    ]
    
    # YELLOW FLAGS - Modify training, but can work around
    YELLOW_FLAG_TERMS = [
        # Inflammation
        "tendonitis", "tendinitis", "tendinopathy",
        "bursitis", "inflammation", "inflamed",
        
        # Minor injuries
        "strain", "sprain", "pull", "pulled",
        "tweak", "tweaked",
        
        # Pain descriptors
        "chronic pain", "ongoing pain", "persistent pain",
        "ache", "aching", "sore", "soreness",
        "stiff", "stiffness", "tight", "tightness",
        
        # Intensity
        "mild pain", "moderate pain", "some pain",
        "discomfort", "uncomfortable",
        
        # Time-based
        "flare up", "flare-up", "aggravated",
        "recent injury", "old injury", "previous injury"
    ]
    
    # Body region keywords
    REGION_MAP = {
        "knee": [
            "knee", "kneecap", "patella", "patellar",
            "acl", "mcl", "lcl", "pcl", "meniscus"
        ],
        "shoulder": [
            "shoulder", "rotator cuff", "rotator",
            "ac joint", "labrum", "deltoid"
        ],
        "back": [
            "back", "lower back", "upper back",
            "spine", "spinal", "lumbar", "thoracic",
            "disc", "disk", "vertebra", "l4", "l5"
        ],
        "ankle": [
            "ankle", "achilles", "achilles tendon",
            "foot", "heel"
        ],
        "wrist": [
            "wrist", "hand", "forearm",
            "carpal", "tfcc"
        ],
        "neck": [
            "neck", "cervical", "trap", "trapezius"
        ],
        "elbow": [
            "elbow", "tennis elbow", "golfer's elbow",
            "tricep tendon", "bicep tendon"
        ],
        "hip": [
            "hip", "groin", "hip flexor",
            "glute", "gluteal", "piriformis"
        ]
    }
    
    # Specific injury types for better classification
    INJURY_TYPES = {
        "patellar tendonitis": {"region": "knee", "severity": "yellow"},
        "achilles tendonitis": {"region": "ankle", "severity": "yellow"},
        "rotator cuff tendonitis": {"region": "shoulder", "severity": "yellow"},
        "tennis elbow": {"region": "elbow", "severity": "yellow"},
        "golfer's elbow": {"region": "elbow", "severity": "yellow"},
        "it band syndrome": {"region": "knee", "severity": "yellow"},
        "plantar fasciitis": {"region": "ankle", "severity": "yellow"},
        "shin splints": {"region": "ankle", "severity": "yellow"},
        
        "acl tear": {"region": "knee", "severity": "red"},
        "meniscus tear": {"region": "knee", "severity": "red"},
        "rotator cuff tear": {"region": "shoulder", "severity": "red"},
        "labrum tear": {"region": "shoulder", "severity": "red"},
        "herniated disc": {"region": "back", "severity": "red"},
        "stress fracture": {"region": "unspecified", "severity": "red"},
    }
    
    def classify(self, injury_text: str) -> InjuryStatus:
        """
        Classify an injury description into severity and region
        
        Args:
            injury_text: User's description of their injury
            
        Returns:
            InjuryStatus object with classification
        """
        
        text = injury_text.lower().strip()
        
        # Initialize status
        status = InjuryStatus(description=injury_text)
        
        # 1. Check for specific known injuries first
        for injury_name, info in self.INJURY_TYPES.items():
            if injury_name in text:
                status.region = info["region"]
                status.severity = info["severity"]
                status.injury_type = injury_name
                return status
        
        # 2. Detect body region
        status.region = self._detect_region(text)
        
        # 3. Determine severity based on keywords
        # RED takes absolute priority
        if self._contains_red_flags(text):
            status.severity = "red"
            status.injury_type = self._extract_injury_type(text)
            return status
        
        # YELLOW if specific terms present
        if self._contains_yellow_flags(text):
            status.severity = "yellow"
            status.injury_type = self._extract_injury_type(text)
            return status
        
        # If region detected but no severity flags, default to yellow (cautious)
        if status.region != "unspecified":
            status.severity = "yellow"
        
        # 4. Extract pain level if mentioned
        status.pain_level = self._extract_pain_level(text)
        
        # If pain level is very high, escalate to red
        if status.pain_level and status.pain_level >= 8:
            status.severity = "red"
        
        # 5. Check if diagnosed
        if any(word in text for word in ["diagnosed", "doctor said", "doctor told me", "physician"]):
            status.diagnosed = True
        
        status.injury_type = self._extract_injury_type(text)
        
        return status
    
    def _detect_region(self, text: str) -> str:
        """Detect injured body region from text"""
        for region, keywords in self.REGION_MAP.items():
            if any(keyword in text for keyword in keywords):
                return region
        return "unspecified"
    
    def _contains_red_flags(self, text: str) -> bool:
        """Check if text contains red flag terms"""
        return any(flag in text for flag in self.RED_FLAG_TERMS)
    
    def _contains_yellow_flags(self, text: str) -> bool:
        """Check if text contains yellow flag terms"""
        return any(flag in text for flag in self.YELLOW_FLAG_TERMS)
    
    def _extract_pain_level(self, text: str) -> Optional[int]:
        """Extract pain level (1-10) from text"""
        # Look for patterns like "8/10", "8 out of 10", "pain level 8"
        patterns = [
            r"(\d+)\s*[/]?\s*(?:out of)?\s*10",
            r"pain level\s*(\d+)",
            r"(\d+)\s*pain",
            r"pain\s*(?:is\s*)?(\d+)"
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                level = int(match.group(1))
                if 1 <= level <= 10:
                    return level
        
        return None
    
    def _extract_injury_type(self, text: str) -> str:
        """Extract the specific injury type mentioned"""
        # Check common injury patterns
        common_injuries = [
            "tendonitis", "tendinitis", "strain", "sprain",
            "tear", "fracture", "inflammation", "bursitis",
            "impingement", "syndrome"
        ]
        
        for injury in common_injuries:
            if injury in text:
                return injury
        
        return "injury"
    
    def get_training_recommendations(self, status: InjuryStatus) -> Dict[str, any]:
        """
        Get training recommendations based on injury status
        
        Args:
            status: InjuryStatus object
            
        Returns:
            Dictionary with recommendations
        """
        
        if status.severity == "red":
            return {
                "can_train": False,
                "recommendation": "Seek medical attention before training",
                "modifications": [],
                "cautions": [
                    "Do not train until cleared by medical professional",
                    "Risk of worsening injury",
                    "May require imaging or professional diagnosis"
                ]
            }
        
        elif status.severity == "yellow":
            return {
                "can_train": True,
                "recommendation": f"Train with modifications to avoid {status.region} stress",
                "modifications": [
                    f"Avoid exercises that load {status.region} heavily",
                    "Use pain-free range of motion only",
                    "Stop if pain increases",
                    "Focus on alternative movement patterns"
                ],
                "cautions": [
                    "Monitor pain levels closely",
                    "See a doctor if pain worsens",
                    "Progress slowly and cautiously"
                ]
            }
        
        else:  # green
            return {
                "can_train": True,
                "recommendation": "Full training with normal precautions",
                "modifications": [],
                "cautions": [
                    "Standard warm-up and progression",
                    "Listen to your body"
                ]
            }
    
    def assess_exercise_safety(
        self, 
        exercise_name: str, 
        injury_status: InjuryStatus
    ) -> Dict[str, any]:
        """
        Assess if a specific exercise is safe given an injury
        
        Args:
            exercise_name: Name of the exercise
            injury_status: InjuryStatus object
            
        Returns:
            Safety assessment dictionary
        """
        
        if injury_status.severity == "green":
            return {
                "safe": True,
                "risk_level": "low",
                "recommendation": "Exercise as normal"
            }
        
        exercise_lower = exercise_name.lower()
        region = injury_status.region
        
        # Define risky patterns for each region
        risky_patterns = {
            "knee": ["squat", "lunge", "jump", "run", "leg press"],
            "shoulder": ["press", "overhead", "bench", "dip"],
            "back": ["deadlift", "squat", "row", "good morning"],
            "ankle": ["run", "jump", "calf", "hop"],
            "wrist": ["press", "curl", "extension", "push"],
            "elbow": ["curl", "extension", "press", "row"]
        }
        
        if region in risky_patterns:
            if any(pattern in exercise_lower for pattern in risky_patterns[region]):
                return {
                    "safe": False,
                    "risk_level": "high",
                    "recommendation": f"Avoid - high stress on {region}"
                }
        
        return {
            "safe": True,
            "risk_level": "low",
            "recommendation": "Should be safe with proper form"
        }
