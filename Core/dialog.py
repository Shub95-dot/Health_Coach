# %%
from dataclasses import dataclass, field
from typing import Dict, Any, Optional

from Core.nlu import NLU
from Core.memory import MemoryStore, UserProfile
from workout_engine import PlanGenerator, ProfileParser #check file names before importing if they are the same in my prototype

class SessionState:
    current_flow: Optional[str] = None
    awaiting: Optional[str] = None
    feature_params: Dict[str, Any] = filed(default_factory=dict)

class DialogManager:

    def __init__(
            self,
            nlu:NLU,
            memory: MemoryStore,
            plan_generator: PlanGenerator,
            profile_parser: ProfileParser
    ):
        self.nlu = nlu
        self.memory = memory
        self.plan_generator = plan_generator
        self.profile_parser = profile_parser
        self.sessions: Dict[str, SessionState] = {}

    def _get_session(self, user_id: str) -> SessionState:
        if user_id not in self.sessions:
            self.sessions[user_id] = SessionState()
        return self.sessions[user_id]
    
    def _map_intent_to_feature(self, intent_tag: Optional[str]) -> Optional[str]:
        if not intent_tag:
            return None
        
        workout_plan_intents = {"workout_plan", "plan", "program"}
        quick_workout_intents = {"quick_workout", "short_workout", "express_session"}
        nutrition_intents = {"nutrition", "diet", "food", "meal_plan"}
        sleep_intents = {"sleep", "rest"}
        pregnancy_intents = {"pregnancy","prenatal"}
        cycle_intents = {"cycle", "menstrual", "period"}
        injury_intents = {"injury", "pain", "hurt"}

        if intent_tag in workout_plan_intents:
            return "multi_week_plan"
        if intent_tag in quick_workout_intents:
            return "quick_workout"
        if intent_tag in nutrition_intents:
            return "nutrition"
        if intent_tag in sleep_intents:
            return "sleep0"
        if intent_tag in pregnancy_intents:
            return "pregnancy"
        if intent_tag in cycle_intents:
            return "cycle"
        if intent_tag in injury_intents:
            return "injury"
        return None

    def _missing_plan_parameters(self, profile: UserProfile, params: Dict[str, Any]) -> list[str]:
        needed = ["goal","dureation_weeks","location", "time_minutes","experience"]
        missing: list[str] = []
        for key in needed:
            value = params.get(key) or getattr(profile, key , None)
            if value is None:
                missing.append(key)
        return missing
    
    def _summarize_request(self, profile: UserProfile, params: Dict[str, Any]) -> str:
        goal = params.get("goal") or profile.goal or "unspecified goal"
        duration = params.get("duration_weeks") or profile.duration_weeks or "unspecified duration"
        location = params.get("location") or profile.location or "home/gym not specified"
        time_min = params.get("time_minutes") or profile.time_minutes or "a flexible session length"
        experience = params.get("experience") or profile.experience or "unspecified experience level"
        injury = params.get("injury") or profile.injury
        pregnant = params.get("pregnant") or profile.pregnant
        cycle_phase = params.get("cycle_phase") or profile.cycle_phase

        lines = ["Here is what i understand so far:"]
        lines.append(f"- Goal:{goal}")
        if isinstance(duration, (int,float)):
            lines.append(f"- Duration: {duration} weeks")
        else:
            lines.append(f" - Duration: {duration}")
        if isinstance(time_min, (int, float)):
            lines.append(f"- Session length: {time_min} minutes")
        else:
            lines.append(f"- Session length: {time_min}")
        lines.append(f"- Training location: {location}")
        lines.append(f"- Experience: {experience}")

        if injury:
            lines.append(f"- Injury / pain: {injury}")
        if pregnant:
            lines.append(f"- Pregnancy: yes (we will keep things medically conservative).")
        if cycle_phase:
            lines.append(f"- Menstrual cycle phase: {cycle_phase}")
        lines.append("")
        lines.append("Is this correct? (yes / no)")
        return "\n".join(lines)
    
    def process_message(self, user_id: str, message:str) -> str:
        message = message.strip()
        session = self._get_session(user_id)

        #load or create profile
        profile = self.memory.load_profile(user_id)

        #Parse structured info from text and merge into profile
        parsed = self.profile_parser.parse(message)
        profile = self.memory.merge_parsed_into_profile(profile, parsed)

        #NLU predict intent
        intent_tag, intent_conf = self.nlu.get_top_intent(message, threshold = 0.6)
        feature_from_intent = self._map_intent_to_feature(intent_tag)

        #If no active flow yet than start from intent if possible
        if session.current_flow == feature_from_intent:
            session.current_flow = feature_from_intent
        
        #Handle confirmation if we are in plan confirmation step

        if session.current_flow == "multi_week_plan" and session.awaiting == "confirm_plan":
            lowered = message.lower()
            if lowered in {"yes","yeah","yep","correct","ok","okay"}:
                #Generate the plan
                text = self._generate_multi_week_plan(profile, session.feature_params)
                session.current_flow = None
                session.awaiting = None
                self.memory.save_profile(profile)
                return text
            elif lowered in {"no","nope","incorrect"}:
                session.feature_params.clear()
                session.awaiting = None
                self.memory.save_profile(profile)
                return "No problem. Tell me again your main goal, duration and where you train"
            
            # Route based on current flow
        if session.current_flow == "multi_week_plan":
            reply = self._handle_multi_week_flow(profile, session , message)
            self.memory.save_profile(profile)
            return reply
        
        if session.current_flow == "quick_workouts":
            reply = self._handle_quick_workout_flow(profile, session, message)
            self.memory.save_profile(profile)
            return reply
        
        #TODO: later nutrition sleep pregnancy cycle injury flows.

        if feature_from_intent == "nutrition":
            return "I can absolutely help with nutrition, but right now lets focus on workouts first. We'll wire a full nutrition module next."
        if feature_from_intent == "sleep":
            return "Sleep coaching is on the roadmap. For now, aim for consistent bed/ wake times, a dark cool room, and limit screen time 60 minutes before bed."
        if feature_from_intent == "pregnancy":
            return "Pregnancy training needs to be medically conservative. We'll build a dedicated pregnancy module with trimester-specific plans next."
        if feature_from_intent == "cycle":
            return "Cycle-aware training is coming - with different approaches for follicular, ovulatory, luteal, and menstrual phases."
        if feature_from_intent == "injury":
            return "If you have pain or injury, please describe it in detail. Severe pain, fractures, tears, or post-surgery should go to a medical professional before training."
        
       #If no clear flow, offer guidance and examples
        return (
            "Tell me what you want to work on.\n"
            "- For a multi-week plan: 'I want a 12-week hypertrophy plan at the gym.'\n"
            "- For a quick workout: 'Give me a 20-minute fat loss workout at home.'\n"
            "- Or tell me about your injuries, pregnancy, or menstrual cycle and we'll adapt training around that."
        )

        #Flow handlers
    
    def _habdle_multi_week_flow(self, profile: UserProfile, session: SessionState, message: str) -> str:
        #update feature_params from parsed again in case user just added info
        parsed = self.profile_parser.parse(message)
        for k, v in parsed.items():
            if v is not None:
                session.feature_params[f] = v
        
        missing = self._missing_plan_parameters(profile, session.feature_params)
        if missing:
            next_param = missing[0]
            session.awaiting = next_param

            if next_param == "goal":
                return "What is your main goal? (falt loss/ muscle gain / general health / performance enhancement / competition prep)"
            if next_param == "duration_weeks":
                return "How many weeks do you want this plan to last?"
            if next_param == "location":
                return "Where will you train? (home / gym / both)"
            if next_param == "time_minutes":
                return "Roughly how many minutes per session do you have ? (e.g. 30, 45, 60, 90, 120)"
            if next_param == "experience":
                return "How would you describe your experience level?(begineer / intermediate / advanced)"
            
            #if nothing missing, ask confirmation
        session.awaiting = "confirm_plan"
        return self._summarize_request(profile, session.feature_params)
    
    def _generate_multi_week_plan(self, profile: UserProfile, params: Dict[str, Any]) -> str:

        #merge profile into params where missing
        effective = dict(params)
        for key in ["goal","duration_weeks", "location", "time_minutes", "experience", "injury",
                    "pregnant", "cycle_phase"]:
            if key not in effective or effective[key] is None:
                effective[key] = getattr(profile, key, None)
        return self.plan_generator.generate_multiweek_plan(profile=profile,params=effective)
    
    def _handle_quick_workout_flow(self, profile: UserProfile, session: SessionState, message: str) -> str:

        parsed = self.profile_parser.parse(message)
        for k, v in parsed.items():
            if v is not None:
                session.feature_params[k] = v
        
        needed = ["goal", "time_minutes", "location"]
        missing = [k for k in needed if not (session.feature_params.get(k) or getattr(profile, k, None))]

        if missing:
            next_param = missing[0]
            session.awaiting = next_param

            if next_param == "goal":
                return "What's your goal for this wuick session? (fat loss / strength / conditioning / mobility)"
            if next_param == "time_minutes":
                return "How many minutes do you have for this workout?"
            if next_param == "location":
                return "Are you training at home or at gym?"
            
            #Generate quick workout
            effective = dict(session.feature_params)
            for key in ["goal", "time_minutes", "location", "injury", "pregnant", "cycle_phase"]:
                if key not in effective or effective[key] is None:
                    effective[key] = getattr(profile, key, None)
            workout_text = self.plan_generator.generate_quick_workout(profile=profile, params=effective)
            session.current_flow = None
            session.awaiting = None
            session.feature_params.clear()
            return workout_text


# %%


# %%



