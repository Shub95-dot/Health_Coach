"""
Complete Health & Fitness Chatbot
Natural conversation with injury adaptation and personalized programming
"""

import json
import os
from typing import Dict, Optional, List
from dataclasses import dataclass, asdict, field
from datetime import datetime

# Import all components
from conversation_engine import ConversationEngine, ResponseFormatter, create_workout_intro, create_injury_modification_intro
from injury_engine import InjuryEngine, InjuryStatus
from injury_adaptation import InjuryAdaptationEngine
from workout_engine import PlanGenerator, ProfileParser, HealthCalculator
from exceptions import MedicalReferralRequired
from ollama_engine import OllamaEngine


@dataclass
class UserProfile:
    """Complete user profile with all attributes"""
    user_id: str
    
    # Basic info
    name: Optional[str] = None
    age: Optional[int] = None
    sex: Optional[str] = None
    height_cm: Optional[float] = None
    weight_kg: Optional[float] = None
    
    # Training parameters
    goal: Optional[str] = None
    duration_weeks: Optional[int] = None
    experience: Optional[str] = None
    location: Optional[str] = None
    time_minutes: Optional[int] = None
    
    # Injury status
    injury_region: Optional[str] = None
    injury_severity: Optional[str] = None
    injury_description: Optional[str] = None
    
    # Metadata
    last_updated: Optional[str] = None
    conversation_count: int = 0
    chat_history: List[Dict[str, str]] = field(default_factory=list)


@dataclass
class SessionState:
    """Track conversation state"""
    user_id: str
    current_flow: Optional[str] = None  # multi_week_plan, injury_query, etc.
    collected_params: Dict[str, any] = field(default_factory=dict)
    awaiting_field: Optional[str] = None
    last_message_time: Optional[str] = None


class MemoryStore:
    """Handle profile and session persistence"""
    
    def __init__(self, profiles_dir: str = "./profiles"):
        self.profiles_dir = profiles_dir
        os.makedirs(profiles_dir, exist_ok=True)
    
    def _profile_path(self, user_id: str) -> str:
        """Get file path for user profile"""
        # Clean user_id for file system
        clean_id = user_id.replace('@', '_at_').replace('.', '_')
        return os.path.join(self.profiles_dir, f"{clean_id}.json")
    
    def load_profile(self, user_id: str) -> UserProfile:
        """Load user profile or create new one"""
        path = self._profile_path(user_id)
        
        if os.path.exists(path):
            with open(path, 'r') as f:
                data = json.load(f)
            return UserProfile(**data)
        
        return UserProfile(user_id=user_id)
    
    def save_profile(self, profile: UserProfile) -> None:
        """Save user profile"""
        profile.last_updated = datetime.utcnow().isoformat()
        path = self._profile_path(profile.user_id)
        
        with open(path, 'w') as f:
            json.dump(asdict(profile), f, indent=2)
    
    def load_session(self, user_id: str) -> SessionState:
        """Load session state"""
        # Session state is currently transient per startup, 
        # but could be made persistent here if needed.
        return SessionState(user_id=user_id)
    
    def save_session(self, session: SessionState) -> None:
        """Save session state (transient in this version)"""
        session.last_message_time = datetime.utcnow().isoformat()


class DialogManager:
    """Manage conversation flow and responses"""
    
    REQUIRED_PLAN_FIELDS = ["goal", "duration_weeks", "experience", "location", "time_minutes"]
    
    def __init__(self, llm_engine=None):
        self.conversation = ConversationEngine(llm_engine=llm_engine)
        self.formatter = ResponseFormatter()
        self.injury_engine = InjuryEngine()
        self.injury_adapter = InjuryAdaptationEngine()
        self.planner = PlanGenerator()
        self.parser = ProfileParser()
    
    def process_message(
        self, 
        user_id: str,
        message: str,
        profile: UserProfile,
        session: SessionState
    ) -> str:
        """
        Process incoming message and generate response
        
        Args:
            user_id: User identifier
            message: User's message
            profile: User profile
            session: Session state
            
        Returns:
            Natural language response
        """
        
        msg = message.lower().strip()
        
        # Handle greetings
        # Handle greetings
        if self._is_greeting(msg) and session.current_flow is None:
            response = self.conversation.generate_greeting()
            profile.chat_history.append({"role": "user", "content": message})
            profile.chat_history.append({"role": "assistant", "content": response})
            return response
        
        # Check for injury mentions
        if self._mentions_injury(msg):
            response = self._handle_injury(msg, profile, session)
            profile.chat_history.append({"role": "user", "content": message})
            profile.chat_history.append({"role": "assistant", "content": response})
            return response
        
        # If in plan collection flow, continue collecting
        # If in plan collection flow, continue collecting
        if session.current_flow == "collecting_plan_params":
            response = self._continue_plan_collection(msg, profile, session)
            profile.chat_history.append({"role": "user", "content": message})
            profile.chat_history.append({"role": "assistant", "content": response})
            return response
        
        # 1. Sync profile data into session params (from UI updates)
        for field_name in self.REQUIRED_PLAN_FIELDS + ["age", "sex", "height_cm", "weight_kg"]:
            if hasattr(profile, field_name):
                val = getattr(profile, field_name)
                if val:
                    session.collected_params[field_name] = val

        # 2. Parse message for new profile data from chat
        parsed_data = self.parser.parse_free_text(message)
        for key, value in parsed_data.items():
            if hasattr(profile, key):
                setattr(profile, key, value)
                session.collected_params[key] = value

        # Check if user wants a plan
        # Check if user wants a plan
        # Bypass for "Smart Suggestion" system prompts
        if self._wants_workout_plan(msg) and "sys_req" not in msg:
            response = self._start_plan_collection(profile, session)
            profile.chat_history.append({"role": "user", "content": message})
            profile.chat_history.append({"role": "assistant", "content": response})
            return response
        
        # If we have all params, generate plan
        if self._has_all_plan_params(session):
            plan_response = self._generate_plan(profile, session)
            profile.chat_history.append({"role": "user", "content": message})
            profile.chat_history.append({"role": "assistant", "content": plan_response})
            return plan_response
        
        # Use LLM for more natural fallback/generic conversation
        profile_context = (
            f"User Profile: {profile.name or 'User'}. "
            f"Goal: {profile.goal or 'Unknown'}. "
            f"Level: {profile.experience or 'Unknown'}. "
            f"Location: {profile.location or 'Unknown'}. "
            f"Age: {profile.age or 'N/A'}. "
            f"Weight: {profile.weight_kg or 'N/A'}kg. "
            f"Height: {profile.height_cm or 'N/A'}cm. "
        )
        
        # Add live metrics if available
        calc = HealthCalculator()
        if profile.weight_kg and profile.height_cm:
            bmi = calc.calculate_bmi(profile.weight_kg, profile.height_cm)
            profile_context += f"BMI: {bmi:.1f} ({calc.get_bmi_category(bmi)}). "
            
        response = self.conversation.get_llm_response(message, profile_context, history=profile.chat_history)
        
        # Store in history
        profile.chat_history.append({"role": "user", "content": message})
        profile.chat_history.append({"role": "assistant", "content": response})
        
        return response
    
    def _is_greeting(self, msg: str) -> bool:
        """Check if message is a greeting"""
        greetings = ['hi', 'hello', 'hey', 'sup', 'yo', 'greetings', 'good morning', 'good afternoon']
        return any(msg.startswith(g) for g in greetings) or msg in greetings
    
    def _mentions_injury(self, msg: str) -> bool:
        """Check if message mentions an injury"""
        injury_keywords = [
            'injury', 'injured', 'pain', 'hurt', 'hurts', 'sore',
            'tear', 'torn', 'sprain', 'strain', 'fracture',
            'tendonitis', 'cannot walk', "can't move"
        ]
        return any(keyword in msg for keyword in injury_keywords)
    
    def _wants_workout_plan(self, msg: str) -> bool:
        """Check if user wants a workout plan"""
        plan_keywords = [
            'workout', 'plan', 'program', 'routine',
            'build muscle', 'lose fat', 'get stronger',
            'train', 'exercise', 'fitness'
        ]
        return any(keyword in msg for keyword in plan_keywords)
    
    def _handle_injury(self, msg: str, profile: UserProfile, session: SessionState) -> str:
        """Handle injury mentions"""
        
        # Classify the injury
        injury_status = self.injury_engine.classify(msg)
        
        # Update profile
        profile.injury_region = injury_status.region
        profile.injury_severity = injury_status.severity
        profile.injury_description = injury_status.description
        
        # Handle based on severity
        if injury_status.severity == "red":
            # Medical referral required
            raise MedicalReferralRequired(
                self.conversation.respond_to_injury(
                    "red",
                    injury_status.region,
                    injury_status.injury_type
                )
            )
        
        elif injury_status.severity == "yellow":
            # Can train with modifications
            response = self.conversation.respond_to_injury(
                "yellow",
                injury_status.region,
                injury_status.injury_type
            )
            
            # Start plan collection
            session.current_flow = "collecting_plan_params"
            
            return response
        
        else:
            # Need more information
            return self.conversation.respond_to_injury(
                "green",
                injury_status.region
            )
    
    def _start_plan_collection(self, profile: UserProfile, session: SessionState) -> str:
        """Start collecting plan parameters"""
        
        session.current_flow = "collecting_plan_params"
        
        # Check what we already know
        missing = self._get_missing_fields(session)
        
        if not missing:
            return self._generate_plan(profile, session)
        
        # Ask for first missing field
        response = self.conversation.acknowledge_positive() + " "
        response += self.conversation.ask_for_info(missing[0])
        session.awaiting_field = missing[0]
        
        return response
    
    def _continue_plan_collection(self, msg: str, profile: UserProfile, session: SessionState) -> str:
        """Continue collecting plan parameters"""
        
        # Parse the message
        parsed = self.parser.parse_free_text(msg)
        
        # Update session
        session.collected_params.update(parsed)
        
        # Check if we have everything
        missing = self._get_missing_fields(session)
        
        if not missing:
            # Generate plan
            return self._generate_plan(profile, session)
        
        # Ask for next field
        response = self.conversation.acknowledge_positive() + " "
        response += self.conversation.ask_for_info(missing[0])
        session.awaiting_field = missing[0]
        
        return response
    
    def _get_missing_fields(self, session: SessionState) -> list:
        """Get list of missing required fields"""
        return [
            field for field in self.REQUIRED_PLAN_FIELDS
            if field not in session.collected_params
        ]
    
    def _has_all_plan_params(self, session: SessionState) -> bool:
        """Check if all plan parameters are collected"""
        return all(
            field in session.collected_params
            for field in self.REQUIRED_PLAN_FIELDS
        )
    
    def _ask_next_question(self, profile: UserProfile, session: SessionState) -> str:
        """Ask for the next piece of information"""
        
        missing = self._get_missing_fields(session)
        
        if missing:
            return self.conversation.ask_for_info(missing[0])
        
        return self.conversation.handle_unclear()
    
    def _generate_plan(self, profile: UserProfile, session: SessionState) -> str:
        """Generate the complete workout plan"""
        
        # Update profile from session
        for key, value in session.collected_params.items():
            if hasattr(profile, key):
                setattr(profile, key, value)
        
        # Get parameters
        params = session.collected_params
        
        # Announce generation
        response = self.conversation.announce_plan_generation(
            params.get('duration_weeks', 8),
            params.get('goal', 'fitness')
        ) + "\n\n"
        
        # Generate plan
        plan = self.planner.generate_multiweek_plan(profile, params)
        
        # If there's an injury, modify the plan
        if profile.injury_region and profile.injury_severity == "yellow":
            # Extract exercises from plan
            # This is simplified - in production you'd parse the plan properly
            modification_result = {
                "removed_count": 3,
                "added_count": 3,
                "removed_exercises": ["Heavy squat", "Jump squat", "Running"],
                "added_exercises": ["Romanian deadlift", "Hip thrust", "Cycling"]
            }
            
            injury_status = InjuryStatus(
                region=profile.injury_region,
                severity=profile.injury_severity,
                description=profile.injury_description or ""
            )
            
            # Add modification summary
            mod_summary = self.injury_adapter.create_modification_summary(
                modification_result,
                injury_status
            )
            
            response += mod_summary + "\n\n"
        
        # Add plan
        response += self.conversation.present_plan()
        response += plan
        
        # Add encouragement
        response += "\n\n" + self.conversation.add_encouragement()
        
        # Clear session
        session.current_flow = None
        session.collected_params.clear()
        
        return response


class HealthWellnessChatbot:
    """
    Main chatbot class - Natural, conversational fitness coach
    """
    
    def __init__(self):
        self.llm = OllamaEngine()
        self.memory = MemoryStore()
        self.dialog = DialogManager(llm_engine=self.llm)
    
    def process_message(self, user_id: str, message: str) -> str:
        """
        Process a message and return response
        
        Args:
            user_id: Unique user identifier (phone number for WhatsApp)
            message: User's message
            
        Returns:
            Natural language response
        """
        
        try:
            # Load user data
            profile = self.memory.load_profile(user_id)
            session = self.memory.load_session(user_id)
            
            # Update conversation count
            profile.conversation_count += 1
            
            # Process message
            response = self.dialog.process_message(
                user_id, message, profile, session
            )
            
            # Save updates
            self.memory.save_profile(profile)
            self.memory.save_session(session)
            
            # Store in history is already done in dialog.process_message
            
            # Return full response for web/cli (chunking is only for specific adapters)
            return response
            
        except MedicalReferralRequired as e:
            # Handle medical referral
            return str(e)
        
        except Exception as e:
            # Handle errors gracefully
            return (
                "Oops! Something went wrong on my end. 😅\n\n"
                "Can you try rephrasing that? Or if you're starting fresh, "
                "just say 'hi' and we'll begin again!"
            )


# CLI Interface for testing
def run_cli():
    """Run chatbot in command line for testing"""
    
    print("\n" + "="*60)
    print("💪 HEALTH & FITNESS AI COACH")
    print("="*60)
    print("\nYour personal fitness coach is ready!")
    print("Type 'quit' to exit\n")
    print("-"*60 + "\n")
    
    bot = HealthWellnessChatbot()
    user_id = "cli_test_user"
    
    while True:
        try:
            user_input = input("You: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'bye']:
                print("\nCoach: Keep crushing it! 💪 See you next time!\n")
                break
            
            if not user_input:
                continue
            
            response = bot.process_message(user_id, user_input)
            print(f"\nCoach: {response}\n")
            print("-"*60 + "\n")
            
        except KeyboardInterrupt:
            print("\n\nCoach: Keep crushing it! 💪 See you next time!\n")
            break
        except Exception as e:
            print(f"\nError: {e}\n")


if __name__ == "__main__":
    run_cli()
