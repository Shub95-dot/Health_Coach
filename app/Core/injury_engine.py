from typing import Dict, List
from app.Core.schemas import InjuryStatus


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

    def classify(self, text: str) -> InjuryStatus:
        text = text.lower()

        status = InjuryStatus()

        # Region detection
        for region, terms in self.REGION_MAP.items():
            if any(t in text for t in terms):
                status.region = region

        # Severity detection
        if any(t in text for t in self.RED_FLAG_TERMS):
            status.severity = "red"
        elif any(t in text for t in self.YELLOW_FLAG_TERMS):
            status.severity = "yellow"
        else:
            if status.region:
                status.severity = "yellow"

        status.description = text
        return status
