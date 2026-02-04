# %%
from typing import List



class InjuryAdaptationEngine:

    REGION_EXERCISE_BLOCKS = {

        "knee": [
            "jump squat",
            "jump",
            "lunge",
            "plyometric",
            "box jump",
            "running",
            "squat",
            "deep squat",
            "heavy lunge"
        ],

        "shoulder": [
            "overhead press",
            "snatch",
            "heavy bench press",
            "upright row"
        ],

        "back": [
            "heavy deadlift",
            "good morning heavy",
            "barbell row heavy"
        ]
    }

    REGION_REPLACEMENTS = {

        "knee": [
            "romanian deadlift",
            "hip thrust",
            "step ups",
            "leg extension light",
            "cycling"
        ],

        "shoulder": [
            "landmine press",
            "cable chest press neutral grip",
            "lateral raise light",
            "face pull"
        ],

        "back": [
            "glute bridge",
            "bird dog",
            "reverse hyper light",
            "core stability work"
        ]
    }

    def modify_exercise_list(self, exercises: List[str], region: str) -> List[str]:

        if region not in self.REGION_EXERCISE_BLOCKS:
            return exercises

        blocked = self.REGION_EXERCISE_BLOCKS[region]
        replacements = self.REGION_REPLACEMENTS[region]

        new_list = []

        for ex in exercises:
            if any(b in ex.lower() for b in blocked):
                continue
            new_list.append(ex)

        new_list.extend(replacements[:2])

        return new_list



