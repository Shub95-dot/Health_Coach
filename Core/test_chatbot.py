from chatbot import HealthWellnessChatbot
import traceback

def test_bot():
    try:
        bot = HealthWellnessChatbot()
        user_id = "test_user"
        
        test_messages = [
            "I want to lose fatloss in 8 wks at hm, beg level.", # Shorthand/Typo
            "at gym", # Short answer to location
            "intermediate", # Short answer to exp
            "60 mins", # Short answer to time
            "build muscl", # New goal mid-conversation
            "gim", # Misspelling of gym
            "hi i am just looking for fitness", # Small talk / blurry goal
        ]
        
        for msg in test_messages:
            print(f"User: {msg}")
            reply = bot.process_message(user_id, msg)
            print(f"Bot: {reply}\n")
            
    except Exception:
        traceback.print_exc()

if __name__ == "__main__":
    test_bot()
