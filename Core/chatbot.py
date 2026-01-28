# %%
from Core.nlu import NLU
from Core.memory import MemoryStore
from Core.dialog import DIalogManager
from workout_engine import PlanGenerator, ProfileParser

class healthWellnessChatbot:

    def __init__(self):
        self.nlu = NLU(
            model_path="chatbot_model.keras",
            words_path="words.pkl",
            classes_path="classes.pkl"
        )
        self.memory_store = MemoryStore()
        self.plan_generator = PlanGenerator()
        self.profile_parser = ProfileParser()

        self.dialog = DialogManager(
            nlu=self.nlu,
            memory=self.memory_store,
            plan_generator=self.plan_generator,
            profile_parser=self.profile_parser
        )

    def process_message(self, user_id: str, message: str) -> str:

        return self.dialog.process_message(user_id=user_id, message=message)
    
if __name__ == "__main__":
    bot = healthWellnessChatbot()
    user_id = "cli_user"
    
    print("Health and Fitness Coach Chatbot")
    print("Type 'quit' to exit.\n")

    while True:
        msg = input("You: ").strip()
        if msg.lower() in {"quit" , "exit"}:
            break
        reply = bot.process_message(user_id, msg)
        print(f"Coach: {reply}\n")


