"""
Natural, Human-like Response Generator
Creates conversational, friendly responses that feel like talking to a real coach
"""

import random
from typing import Dict, List, Optional
from dataclasses import dataclass


@dataclass
class ResponseTemplate:
    """Template for generating natural responses"""
    templates: List[str]
    context: str  # greeting, plan_ready, asking_info, injury_concern, etc.
    tone: str  # friendly, encouraging, professional, concerned


class ConversationEngine:
    """Generates human-like, natural responses"""
    
    def __init__(self, llm_engine=None):
        self.llm = llm_engine
    
    # Greeting responses
    GREETINGS = [
        "Hey! Great to see you! 💪 I'm your fitness coach. What brings you here today?",
        "Hi there! Ready to crush some goals? Tell me what you're looking to achieve!",
        "Hello! I'm excited to help you on your fitness journey. What's your main goal right now?",
        "Hey! Welcome! Whether you want to build muscle, lose fat, or just get healthier - I've got you covered. What's on your mind?",
        "Hi! I'm here to create a personalized workout plan just for you. What are you hoping to accomplish?"
    ]
    
    # Asking for basic info
    ASKING_GOAL = [
        "What's your main goal? Are you looking to:\n• Build muscle 💪\n• Lose fat 🔥\n• Get stronger 🏋️\n• Improve endurance 🏃\n• Or something else?",
        "I'd love to know what you're aiming for! Whether it's muscle gain, fat loss, strength, or just getting fitter - let me know!",
        "So what's driving you to train? Tell me your goal and I'll build a plan around it!"
    ]
    
    ASKING_EXPERIENCE = [
        "Got it! Now, how would you describe your training experience?\n• Beginner (new to this)\n• Intermediate (training for a while)\n• Advanced (pretty experienced)",
        "Perfect! Quick question - what's your experience level with working out?",
        "Nice! Are you new to training, or have you been at it for a while?"
    ]
    
    ASKING_LOCATION = [
        "Awesome! Where will you be training?\n• Home 🏠\n• Gym 🏋️",
        "Cool! Do you have access to a gym, or are you training at home?",
        "Perfect! Will you be working out at home or do you have a gym membership?"
    ]
    
    ASKING_DURATION = [
        "Great! How many weeks do you want this program to run? (I'd recommend 8-12 weeks for best results)",
        "Nice! How long do you want to commit? Most people see great results with 8-12 weeks.",
        "Awesome! What timeframe are you thinking? Usually 8-12 weeks works really well."
    ]
    
    ASKING_TIME = [
        "Almost there! How much time do you have per workout? (45-60 minutes is ideal)",
        "Last question - how many minutes can you dedicate to each session?",
        "Perfect! And roughly how long can each workout be?"
    ]
    
    # Injury responses
    INJURY_CONCERN_INITIAL = [
        "I hear you about the {body_part}. Your safety is my top priority. Let me ask a few questions:\n\n• Where exactly does it hurt?\n• How would you rate the pain (1-10)?\n• Was this diagnosed by a doctor?\n• When did it start?",
        "Got it - {body_part} pain. I want to make sure we train safely. Tell me:\n\n• Exact location of the pain?\n• Pain level 1-10?\n• Did you see a doctor about it?\n• How long have you had this?",
        "Okay, let's talk about your {body_part}. Safety first! I need to know:\n\n• Where specifically does it hurt?\n• Pain intensity (1-10)?\n• Any medical diagnosis?\n• How recent is this?"
    ]
    
    INJURY_RED_FLAG = [
        "⚠️ Hold on - this sounds serious. Based on what you're describing ({injury_desc}), I really think you should see a doctor or physiotherapist before we start training.\n\nThis isn't something to push through. Get it checked out, and once you have clearance, I'll build you the perfect program! 🏥",
        "⚠️ Okay, I need to stop you here. What you're describing sounds like it needs professional medical attention. Please see a doctor before we continue training.\n\nYour health comes first, always. Once you're cleared, come back and we'll get you strong safely! 💙",
        "⚠️ I'm concerned about this. {injury_desc} - this really should be evaluated by a medical professional first.\n\nDon't risk making it worse. See a doctor, get the all-clear, then we'll train smart together!"
    ]
    
    INJURY_YELLOW_FLAG = [
        "Alright, so it sounds like {injury_type} - we can definitely work around this! 👍\n\nHere's the plan:\n✅ I'll remove exercises that stress your {body_part}\n✅ I'll include safe alternatives\n✅ We'll focus on what you CAN do\n✅ You'll still see great results!\n\nBut listen - if the pain gets worse, you stop and see a doctor. Deal?",
        "Okay, I understand. This sounds like {injury_type}. Good news - we can train safely around this!\n\nI'm going to:\n• Avoid movements that aggravate your {body_part}\n• Include proven alternatives\n• Build strength in other areas\n• Keep you progressing!\n\nJust promise me: if it hurts more, you stop and get it checked. Sound good?",
        "Got it - {injury_type}. We can handle this smartly!\n\nI'll modify your program to:\n✓ Skip problematic exercises\n✓ Add {body_part}-friendly movements\n✓ Still get you amazing results\n\nRule: Any sharp pain = stop immediately. We train smart, not stupid! 😉"
    ]
    
    # Plan generation responses
    PLAN_GENERATING = [
        "Awesome! I've got everything I need. Give me a moment to build your personalized {duration} week {goal} program... 🔨",
        "Perfect! Let me put together your custom {duration}-week plan for {goal}... This is gonna be good! 💪",
        "Alright! Building your {goal} program now. {duration} weeks of gains coming right up... ⚡"
    ]
    
    PLAN_READY = [
        "🎉 Your personalized program is ready! Here's what I've built for you:\n\n",
        "💪 Done! I've created your custom training plan:\n\n",
        "🔥 Your program is complete! Check this out:\n\n"
    ]
    
    # Encouragement
    ENCOURAGEMENT = [
        "You've got this! 💪",
        "Let's do this! 🔥",
        "You're going to crush it!",
        "I believe in you! 💯",
        "This is gonna be great!",
        "Ready to transform? Let's go! ⚡"
    ]
    
    # Clarification requests
    UNCLEAR_INPUT = [
        "Hmm, I didn't quite catch that. Could you rephrase? I'm looking for things like your goal (muscle gain, fat loss, etc.), experience level, or where you train.",
        "Sorry, I'm not sure I understood. Can you tell me more? Are you asking about a workout plan, or do you have an injury concern?",
        "I want to help, but I'm not sure what you need. Are you looking to:\n• Create a workout plan\n• Modify training around an injury\n• Get nutrition advice\n• Something else?"
    ]
    
    # Positive reinforcement
    GOOD_CHOICE = [
        "Excellent choice!",
        "Smart!",
        "Perfect!",
        "Great!",
        "Love it!",
        "That's the spirit!"
    ]
    
    @classmethod
    def generate_greeting(cls) -> str:
        """Generate a friendly greeting"""
        return random.choice(cls.GREETINGS)
    
    @classmethod
    def ask_for_info(cls, field: str) -> str:
        """Ask for specific information naturally"""
        field_map = {
            "goal": cls.ASKING_GOAL,
            "experience": cls.ASKING_EXPERIENCE,
            "location": cls.ASKING_LOCATION,
            "duration_weeks": cls.ASKING_DURATION,
            "time_minutes": cls.ASKING_TIME,
        }
        
        templates = field_map.get(field, cls.UNCLEAR_INPUT)
        return random.choice(templates)
    
    @classmethod
    def respond_to_injury(cls, severity: str, body_part: str, injury_type: str = "") -> str:
        """Generate injury-specific response"""
        if severity == "red":
            return random.choice(cls.INJURY_RED_FLAG).format(
                injury_desc=injury_type or "what you described"
            )
        elif severity == "yellow":
            return random.choice(cls.INJURY_YELLOW_FLAG).format(
                injury_type=injury_type or "this injury",
                body_part=body_part
            )
        else:
            return random.choice(cls.INJURY_CONCERN_INITIAL).format(body_part=body_part)
    
    @classmethod
    def announce_plan_generation(cls, duration: int, goal: str) -> str:
        """Announce that plan is being generated"""
        return random.choice(cls.PLAN_GENERATING).format(
            duration=duration,
            goal=goal
        )
    
    @classmethod
    def present_plan(cls) -> str:
        """Introduce the generated plan"""
        return random.choice(cls.PLAN_READY)
    
    @classmethod
    def add_encouragement(cls) -> str:
        """Add encouraging message"""
        return random.choice(cls.ENCOURAGEMENT)
    
    @classmethod
    def handle_unclear(cls) -> str:
        """Handle unclear input"""
        return random.choice(cls.UNCLEAR_INPUT)
    
    @classmethod
    def acknowledge_positive(cls) -> str:
        """Positive acknowledgment"""
        return random.choice(cls.GOOD_CHOICE)

    def get_llm_response(self, user_message: str, profile_context: str = "", history: List[Dict[str, str]] = None) -> str:
        """Use Ollama to generate a natural response with context and history"""
        if not self.llm:
            return self.handle_unclear()
            
        system_prompt = f"""
        You are a friendly and professional Health & Fitness Coach. 
        Your goal is to help users with workout plans and injury management.
        Current User Context: {profile_context}
        Keep responses encouraging, concise, and professional.
        Do not give medical advice beyond safe training modifications.
        """
        
        messages = [{'role': 'system', 'content': system_prompt}]
        
        # Add limited history for context (last 10 messages)
        if history:
            messages.extend(history[-10:])
            
        messages.append({'role': 'user', 'content': user_message})
        
        return self.llm.chat(messages)


class ResponseFormatter:
    """Format responses to be more conversational"""
    
    @staticmethod
    def add_personality(response: str, user_profile=None) -> str:
        """Add personality touches to response"""
        
        # Add name if we know it
        if user_profile and hasattr(user_profile, 'name') and user_profile.name:
            response = f"Hey {user_profile.name}! " + response
        
        return response
    
    @staticmethod
    def chunk_long_response(response: str, max_length: int = 1000) -> List[str]:
        """Break long responses into readable chunks (for WhatsApp)"""
        if len(response) <= max_length:
            return [response]
        
        chunks = []
        current_chunk = ""
        
        for line in response.split('\n'):
            if len(current_chunk) + len(line) + 1 > max_length:
                chunks.append(current_chunk.strip())
                current_chunk = line + '\n'
            else:
                current_chunk += line + '\n'
        
        if current_chunk.strip():
            chunks.append(current_chunk.strip())
        
        return chunks
    
    @staticmethod
    def add_emojis_contextually(text: str, context: str) -> str:
        """Add relevant emojis based on context"""
        emoji_map = {
            "muscle gain": "💪",
            "fat loss": "🔥",
            "strength": "🏋️",
            "endurance": "🏃",
            "injury": "🩹",
            "success": "🎉",
            "warning": "⚠️",
            "gym": "🏋️‍♂️",
            "home": "🏠"
        }
        
        for key, emoji in emoji_map.items():
            if key in text.lower() and emoji not in text:
                # Add emoji at end if not already present
                if context == "goal":
                    text = text.replace(key, f"{key} {emoji}")
        
        return text


# Example usage and helpers
def make_response_natural(technical_response: str, context: str = "general") -> str:
    """
    Convert technical/templated responses into natural conversation
    
    Args:
        technical_response: The raw response from the system
        context: Context of the conversation (greeting, planning, injury, etc.)
    
    Returns:
        Natural, human-like response
    """
    
    # Add conversational connectors
    connectors = {
        "greeting": ["Hey!", "Hi!", "Hello!", "What's up!"],
        "planning": ["Alright,", "Okay,", "Perfect,", "Got it,"],
        "injury": ["I understand.", "I hear you.", "Okay,"],
        "encouragement": ["Nice!", "Awesome!", "Great!", "Perfect!"]
    }
    
    connector = random.choice(connectors.get(context, ["Okay,"]))
    
    # Make it conversational
    response = f"{connector} {technical_response}"
    
    return response


def create_workout_intro(goal: str, weeks: int, experience: str) -> str:
    """Create an engaging intro for a workout plan"""
    
    intros = [
        f"Alright! I've designed a {weeks}-week {goal} program specifically for your {experience} level. This is going to be good! 💪\n\n",
        f"Here we go! Your custom {weeks}-week plan for {goal} is ready. Tailored perfectly for {experience} level. Let's get it! 🔥\n\n",
        f"Done! Built you a {weeks}-week {goal} program. Since you're {experience}, I've calibrated everything just right. Time to transform! ⚡\n\n"
    ]
    
    return random.choice(intros)


def create_injury_modification_intro(injury_region: str, exercises_removed: int, exercises_added: int) -> str:
    """Create reassuring intro for injury-modified plans"""
    
    intros = [
        f"✅ Your program is ready - fully modified to protect your {injury_region}!\n\n"
        f"I've removed {exercises_removed} problematic exercises and added {exercises_added} safe alternatives. "
        f"You'll still make amazing progress! 💪\n\n",
        
        f"🩹 All set! Your {injury_region}-safe program is complete.\n\n"
        f"Removed {exercises_removed} risky movements, added {exercises_added} proven alternatives. "
        f"We're training smart, not reckless! 👍\n\n",
        
        f"💪 Your modified program is ready! I've worked around your {injury_region} injury.\n\n"
        f"{exercises_removed} exercises replaced with {exercises_added} safer options. "
        f"You'll recover AND get stronger! ✅\n\n"
    ]
    
    return random.choice(intros)
