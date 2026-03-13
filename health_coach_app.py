import streamlit as st
import sys
import os

# Add Core to path so we can import the classes
sys.path.append(os.path.join(os.path.dirname(__file__), 'Core'))

from chatbot import HealthWellnessChatbot

# Set page config
st.set_page_config(page_title="Health Coach Chatbot", page_icon="💪", layout="centered")

st.title("💪 Health & Wellness Coach")
st.markdown("""
Welcome! I am your personal fitness and wellness coach. 
I can help you with:
- **Fat Loss & Muscle Gain Plans**
- **Quick Workouts**
- **Injury Adaptation**
- **Cycle & Pregnancy Modifications**
""")

# Initialize chatbot and session state
if "chatbot" not in st.session_state:
    st.session_state.chatbot = HealthWellnessChatbot()

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hi! I'm your training coach. Tell me your goal (e.g., 6-week fat loss plan, home workout, or training with an injury)!"}
    ]

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Sidebar for Stats & Control
with st.sidebar:
    st.header("📊 Your Profile")
    profile = st.session_state.chatbot.memory.load_profile("streamlit_user")
    if profile.name:
        st.write(f"**Name:** {profile.name}")
        st.write(f"**Age:** {profile.age if profile.age else '---'}")
        st.write(f"**Sex:** {profile.sex if profile.sex else '---'}")
        
        h_str = f"{profile.height_cm:.1f} cm" if profile.height_cm else "---"
        w_str = f"{profile.weight_kg:.1f} kg" if profile.weight_kg else "---"
        
        st.write(f"**Height:** {h_str}")
        st.write(f"**Weight:** {w_str}")
        st.divider()
        st.markdown(st.session_state.chatbot.dialog._get_health_stats_text(profile))
    else:
        st.info("Complete onboarding to see your health stats here.")
    
    st.divider()
    if st.button("Reset Chat"):
        st.session_state.messages = [
            {"role": "assistant", "content": "Chat reset. How can I help you today?"}
        ]
        st.rerun()

# React to user input
if prompt := st.chat_input("Ask me anything about your fitness journey..."):
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Get response from chatbot
    user_id = "streamlit_user"
    result = st.session_state.chatbot.process_message(user_id, prompt)
    
    # Robust handling for older chatbot instances (returning strings) vs newer ones (returning dicts)
    if isinstance(result, str):
        response = result
        pdf_path = None
    else:
        response = result.get("reply", "Sorry, I encountered an error.")
        pdf_path = result.get("pdf_path")

    with st.chat_message("assistant"):
        st.markdown(response)
        if pdf_path and os.path.exists(pdf_path):
            with open(pdf_path, "rb") as f:
                st.download_button(
                    label="📄 Download Workout PDF",
                    data=f,
                    file_name=os.path.basename(pdf_path),
                    mime="application/pdf"
                )
    
    st.session_state.messages.append({"role": "assistant", "content": response})
    st.rerun()
