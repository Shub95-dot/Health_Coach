import streamlit as st
import os
import time
from chatbot import HealthWellnessChatbot
from workout_engine import HealthCalculator
from dotenv import load_dotenv

load_dotenv()

# Page config
st.set_page_config(
    page_title="💪 AI Fitness Coach | Premium",
    page_icon="🏋️‍♂️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Premium Theme & CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');

    :root {
        --primary: #00d4ff;
        --secondary: #00ff87;
        --bg-dark: #0e1117;
        --card-bg: rgba(255, 255, 255, 0.05);
    }

    .stApp {
        background-color: var(--bg-dark);
        font-family: 'Inter', sans-serif;
    }

    /* Glassmorphism Sidebar */
    [data-testid="stSidebar"] {
        background-image: linear-gradient(180deg, rgba(0, 212, 255, 0.05) 0%, rgba(0, 255, 135, 0.05) 100%);
        backdrop-filter: blur(10px);
        border-right: 1px solid rgba(255, 255, 255, 0.1);
    }

    /* Gradient Headers */
    .section-header {
        background: linear-gradient(90deg, #00d4ff 0%, #00ff87 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
        font-size: 2rem;
        margin-bottom: 1rem;
    }

    /* Custom Chat Bubbles */
    .stChatMessage {
        border-radius: 20px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
    }

    .stChatMessage[data-testid="stChatMessageAssistant"] {
        background: rgba(0, 212, 255, 0.07);
        border-left: 4px solid var(--primary);
    }

    .stChatMessage[data-testid="stChatMessageUser"] {
        background: rgba(255, 255, 255, 0.03);
        border-right: 4px solid var(--secondary);
    }

    /* Metric Cards */
    .metric-card {
        background: var(--card-bg);
        padding: 1rem;
        border-radius: 12px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        text-align: center;
        margin-bottom: 1rem;
    }

    .metric-value {
        font-size: 1.5rem;
        font-weight: 800;
        color: var(--primary);
    }

    .metric-label {
        font-size: 0.8rem;
        color: #888;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
</style>
""", unsafe_allow_html=True)

# Initialize Chatbot State
if "bot" not in st.session_state:
    st.session_state.bot = HealthWellnessChatbot()

# Login / Identification Logic
if "user_id" not in st.session_state:
    st.markdown('<p class="section-header">💪 Welcome to Your Fitness Journey</p>', unsafe_allow_html=True)
    st.write("Please enter your name or user ID to continue. Your coach will remember your previous conversations and workout progress.")
    
    login_id = st.text_input("Username / ID", key="login_input")
    if st.button("Start Coaching"):
        if login_id.strip():
            st.session_state.user_id = login_id.strip().lower()
            st.rerun()
        else:
            st.warning("Please enter a valid name or ID.")
    st.stop()

# Single Source of Truth for Profile and History
profile = st.session_state.bot.memory.load_profile(st.session_state.user_id)
st.session_state.messages = list(profile.chat_history)

# Header
col1, col2 = st.columns([3, 1])
with col1:
    st.markdown('<p class="section-header">💪 Health & Fitness AI Coach</p>', unsafe_allow_html=True)
with col2:
    if st.button("🚪 Logout / Switch User", use_container_width=True):
        del st.session_state.user_id
        if "messages" in st.session_state:
            del st.session_state.messages
        st.rerun()

# Sidebar: User Profile & Metrics
with st.sidebar:
    st.image("https://img.icons8.com/parakeet/512/fitness.png", width=100)
    st.markdown(f"### 👤 {st.session_state.user_id.title()}'s Dashboard")
    
    profile = st.session_state.bot.memory.load_profile(st.session_state.user_id)
    calc = HealthCalculator()
    
    if profile.weight_kg and profile.height_cm:
        bmi = calc.calculate_bmi(profile.weight_kg, profile.height_cm)
        bmi_cat = calc.get_bmi_category(bmi)
        
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Body Mass Index</div>
            <div class="metric-value">{bmi:.1f}</div>
            <div style="color: { '#00ff87' if bmi_cat == 'Normal' else '#ff4b4b' }">{bmi_cat}</div>
        </div>
        """, unsafe_allow_html=True)

        if profile.age and profile.sex:
            bmr = calc.estimate_bmr(profile.weight_kg, profile.height_cm, profile.age, profile.sex)
            tdee = calc.estimate_tdee(bmr, profile.experience or "beginner", profile.goal)
            
            col_a, col_b = st.columns(2)
            with col_a:
                st.markdown(f'<div class="metric-card"><div class="metric-label">BMR</div><div class="metric-value">{int(bmr)}</div></div>', unsafe_allow_html=True)
            with col_b:
                st.markdown(f'<div class="metric-card"><div class="metric-label">TDEE</div><div class="metric-value">{int(tdee)}</div></div>', unsafe_allow_html=True)

    # Profile Quick Stats
    with st.expander("📝 Personal Record", expanded=True):
        # Name
        new_name = st.text_input("Display Name", value=profile.name or st.session_state.user_id.title())
        
        # Age
        new_age = st.number_input("Age", min_value=10, max_value=100, value=profile.age or 25)
        
        # Sex
        sexes = ["male", "female", "other"]
        current_sex_idx = sexes.index(profile.sex) if profile.sex in sexes else 0
        new_sex = st.selectbox("Sex", sexes, index=current_sex_idx)
        
        # Height & Weight
        new_height = st.number_input("Height (cm)", min_value=50.0, max_value=250.0, value=float(profile.height_cm or 170))
        new_weight = st.number_input("Weight (kg)", min_value=20.0, max_value=300.0, value=float(profile.weight_kg or 70))
        
        # Fitness Parameters
        goals = ["fat loss", "muscle gain", "strength", "endurance", "general health"]
        current_goal_idx = goals.index(profile.goal) if profile.goal in goals else 4
        new_goal = st.selectbox("Fitness Goal", goals, index=current_goal_idx)
        
        levels = ["beginner", "intermediate", "advanced"]
        current_level_idx = levels.index(profile.experience) if profile.experience in levels else 0
        new_level = st.selectbox("Experience Level", levels, index=current_level_idx)
        
        locations = ["gym", "home"]
        current_loc_idx = locations.index(profile.location) if profile.location in locations else 0
        new_location = st.selectbox("Training Location", locations, index=current_loc_idx)

        new_duration = st.number_input("Program Duration (weeks)", min_value=1, max_value=52, value=profile.duration_weeks or 8)
        new_time = st.number_input("Session Time (minutes)", min_value=10, max_value=180, value=profile.time_minutes or 60)

        # Save changes if anything modified
        if (new_name != profile.name or new_age != profile.age or new_sex != profile.sex or 
            new_height != profile.height_cm or new_weight != profile.weight_kg or 
            new_goal != profile.goal or new_level != profile.experience or 
            new_location != profile.location or new_duration != profile.duration_weeks or 
            new_time != profile.time_minutes):
            
            profile.name = new_name
            profile.age = new_age
            profile.sex = new_sex
            profile.height_cm = new_height
            profile.weight_kg = new_weight
            profile.goal = new_goal
            profile.experience = new_level
            profile.location = new_location
            profile.duration_weeks = new_duration
            profile.time_minutes = new_time
            
            st.session_state.bot.memory.save_profile(profile)
            st.rerun()

    if st.button("🤖 Smart Workout Suggestion"):
        suggestion_prompt = "SYS_REQ: Based on my current profile and health stats, give me a smart workout suggestion or coaching tip."
        
        with st.spinner("Analyzing your profile for the best approach..."):
            # The message is now saved to history by the bot internally
            st.session_state.bot.process_message(st.session_state.user_id, suggestion_prompt)
            st.rerun()

# Chat interface
chat_container = st.container()

with chat_container:
    # Always sync with full history from profile
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# Chat Input & Logic
# Chat Input & Logic
if prompt := st.chat_input("Ask about your workout, nutrition, or injury..."):
    # Bot Response
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        placeholder = st.empty()
        
        with st.spinner("Your coach is thinking..."):
            response = st.session_state.bot.process_message(
                st.session_state.user_id, 
                prompt
            )
            
            # Streaming effect
            full_response = ""
            for word in response.split(" "):
                full_response += word + " "
                time.sleep(0.005) # Faster streaming
                placeholder.markdown(full_response + "▌")
            placeholder.markdown(full_response)
    
    st.rerun()
