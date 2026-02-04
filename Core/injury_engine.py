# %%
from typing import List
from schemas import InjuryStatus


class InjuryEngine:
    """
    Classifies injury descriptions into:
    - region (knee, shoulder, back, etc.)
    - severity (green / yellow / red)git 

    This is used by:
    - DialogManager to decide when to stop and send to doctor
    - PlanGenerator / injury_adaptation to modify exercises
    """

    # Terms that indicate potentially serious / red-flag injuries
    RED_FLAG_TERMS: List[str] = [
        "fracture",
        "broken bone",
        "torn ligament",
        "acl tear",
        "acl rupture",
        "meniscus tear",
        "rupture",
        "dislocation",
        "post surgery",
        "post-surgery",
        "post op",
        "post-op",
        "cannot walk",
        "cant walk",
        "unable to walk",
        "cannot bear weight",
        "cant bear weight",
        "severe pain",
        "sharp stabbing pain",
    ]

    # Terms that indicate non-trivial but usually train-around issues
    YELLOW_FLAG_TERMS: List[str] = [
        "tendonitis",
        "tendinitis",
        "tendinopathy",
        "strain",
        "sprain",
        "chronic pain",
        "ongoing pain",
        "flare up",
        "flare-up",
        "tightness",
        "mild pain",
        "ache",
        "aching",
        "soreness",
        "stiffness",
    ]

    # Map from region to keywords that mention that region
    REGION_MAP = {
        "knee": [
            "knee",
            "patella",
            "meniscus",
            "acl",
            "pcl",
            "mcl",
            "lcl",
        ],
        "shoulder": [
            "shoulder",
            "rotator cuff",
            "ac joint",
            "deltoid",
        ],
        "back": [
            "back",
            "lower back",
            "upper back",
            "lumbar",
            "thoracic",
            "spine",
            "disc",
            "herniated disc",
            "slipped disc",
        ],
        "ankle": [
            "ankle",
            "achilles",
            "achilles tendon",
        ],
        "hip": [
            "hip",
            "groin",
        ],
        "wrist": [
            "wrist",
            "carpal",
        ],
        "elbow": [
            "elbow",
            "tennis elbow",
            "golfer's elbow",
            "golfers elbow",
        ],
        "neck": [
            "neck",
            "cervical",
        ],
    }

    def classify(self, text: str) -> InjuryStatus:
        """
        Take a free-text injury description and return InjuryStatus(region, severity).
        - region: one of REGION_MAP keys, or "unspecified"
        - severity: "green", "yellow", or "red"
        """
        text = (text or "").lower()

        # Start with a safe default
        status = InjuryStatus(region="unspecified", severity="green")

        # -------- REGION DETECTION --------
        for region, terms in self.REGION_MAP.items():
            if any(term in text for term in terms):
                status.region = region
                break

        # -------- SEVERITY DETECTION --------
        # RED flags > YELLOW flags > default (green or light yellow if region present)
        if any(term in text for term in self.RED_FLAG_TERMS):
            status.severity = "red"
        elif any(term in text for term in self.YELLOW_FLAG_TERMS):
            status.severity = "yellow"
        elif status.region != "unspecified":
            # Region mentioned but no clear flags → be conservative
            status.severity = "yellow"
        else:
            status.severity = "green"

        # Optional description, if your InjuryStatus has that field
        if hasattr(status, "description"):
            status.description = text

        return status

    # Optional helpers if you want them later
    def has_red_flag(self, text: str) -> bool:
        return any(term in (text or "").lower() for term in self.RED_FLAG_TERMS)

    def has_yellow_flag(self, text: str) -> bool:
        return any(term in (text or "").lower() for term in self.YELLOW_FLAG_TERMS)


# Quick manual test block (you can keep or remove later)
if __name__ == "__main__":
    engine = InjuryEngine()

    examples = [
        "I tore my ACL and cannot walk on my right leg",
        "My knee has mild tendonitis",
        "My lower back feels tight after deadlifts",
        "I have some general soreness in my shoulders",
        "No pain, I just want to train harder",
    ]

    for txt in examples:
        status = engine.classify(txt)
        print(f"Text: {txt}")
        print(f"  -> region={status.region}, severity={status.severity}")
        if hasattr(status, "description"):
            print(f"  -> description={status.description}")
        print("----")


# %%


# %%
from typing import Dict, List
from app.Core.schemas import InjuryStatus
import re
from dataclasses import dataclass

@dataclass
class InjuryStatus:
    region: str
    severity: str  # 'green', 'yellow', 'red'


class InjuryEngine:

    RED_FLAG_TERMS = [
    "fracture",
    "torn ligament",
    "acl tear",
    "acl rupture",
    "rupture",
    "dislocation",
    "post surgery",
    "post-surgery",
    "cannot walk",
    "cant walk",
    "unable to walk",
    "cannot bear weight",
    "cant bear weight"
]

    YELLOW_FLAG_TERMS = [
        "tendonitis",
        "tendinitis",
        "strain",
        "sprain",
        "chronic pain",
        "flare up",
        "tightness",
        "mild pain"
    ]


    REGION_MAP = {
        "knee": ["knee", "acl", "meniscus"],
        "shoulder": ["shoulder", "rotator cuff"],
        "back": ["lower back", "lumbar", "spine"],
        "ankle": ["ankle", "achilles"],
        "wrist": ["wrist"],
        "neck": ["neck", "cervical"]
    }


class InjuryEngine:

    def classify(self, injury_text: str) -> InjuryStatus:
        text = injury_text.lower()

        # Detect region
        region = "unspecified"
        if any(k in text for k in ["knee", "patella", "meniscus"]):
            region = "knee"
        elif any(k in text for k in ["shoulder", "rotator", "ac joint"]):
            region = "shoulder"
        elif any(k in text for k in ["back", "spine", "disc", "lumbar"]):
            region = "back"

        # Determine severity
        red_flags = [
            "fracture", "rupture", "tear", "torn", "dislocation",
            "severe", "broken", "surgery", "post-op"
        ]
        yellow_flags = [
            "pain", "sprain", "strain", "swelling", "ache", "tenderness"
        ]

        severity = "green"  # default
        if any(word in text for word in red_flags):
            severity = "red"
        elif any(word in text for word in yellow_flags):
            severity = "yellow"

        return InjuryStatus(region=region, severity=severity)


    def classify(self, text: str) -> InjuryStatus:
        text = text.lower()

        region = "unspecified"
        if any(k in text for k in ["knee", "patella", "meniscus"]):
            region = "knee"
        elif any(k in text for k in ["shoulder", "rotator", "ac joint"]):
            region = "shoulder"
        elif any(k in text for k in ["back", "spine", "disc", "lumbar"]):
            region = "back"

        severity = "green"
        if any(word in text for word in ["fracture", "rupture", "tear", "torn", "dislocation", "severe", "broken", "surgery", "post-op"]):
            severity = "red"
        elif any(word in text for word in ["pain", "sprain", "strain", "swelling", "ache", "tenderness"]):
            severity = "yellow"

        status = InjuryStatus(region=region, severity=severity)


                # Region detection
        for region, terms in self.REGION_MAP.items():
            if any(t in text for t in terms):
                status.region = region

        # Severity detection
        # RED takes absolute priority
        if any(t in text for t in self.RED_FLAG_TERMS):
            status.severity = "red"

        elif any(t in text for t in self.YELLOW_FLAG_TERMS):
            status.severity = "yellow"

        elif status.region:
            status.severity = "yellow"


        status.description = text
        return status


# %%
engine = InjuryEngine()

text = "I tore my ACL and have severe knee pain"
status = engine.classify(text)

print(status.region)    # Expected: "knee"
print(status.severity)  # Expected: "red"


# %%



