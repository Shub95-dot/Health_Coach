# %%
from chatbot import HealthWellnessChatbot

def main():
    bot = HealthWellnessChatbot()
    user_id = "testing_cli"

    print("Health and Fitness Coach Chatbot")
    print("type 'quit' or 'exit' to leave.\n")

    while True:
        msg = input("You: ").strip()
        if msg.lower() in {"quit", "exit"}:
            print("Coach: Byeeee!")
            break

        reply = bot.process_message(user_id, msg)
        print(f"\nCoach: {reply}\n")

if __name__ == "__main__":
    main()


