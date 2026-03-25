# Health & Fitness AI Chatbot

An intelligent, personalized health and fitness coaching chatbot that creates customized workout plans, handles injuries safely, and adapts to individual user needs.

## 🌟 Features

### Core Capabilities
- **Personalized Workout Plans**: Multi-week programs tailored to goals, experience, and equipment
- **Injury Management**: Smart injury classification with safety-first approach
- **Progressive Overload**: Scientifically-backed progression models
- **Nutrition Guidance**: Calorie and macro calculations based on individual metrics
- **Profile Memory**: Persistent user profiles with conversation history
- **Natural Language Understanding**: Parse user input for seamless interaction

### Safety Features
- **Medical Referral System**: Automatically flags serious injuries requiring professional care
- **Injury Adaptation**: Modifies exercises to avoid problematic movements
- **Red/Yellow/Green Classification**: Three-tier injury severity system
- **Conservative Approach**: Pregnancy and medical condition awareness

### Specialized Support
- **Menstrual Cycle Awareness**: Training adaptation for cycle phases
- **Pregnancy Modifications**: Safe exercise guidelines for prenatal training
- **Experience-Based Programming**: Beginner to advanced level protocols
- **Location Flexibility**: Home or gym-based workouts

## 📋 System Architecture

```
Health & Fitness Chatbot
├── Core Components
│   ├── NLU (Natural Language Understanding)
│   ├── Dialog Manager
│   ├── Memory Store
│   ├── Workout Engine
│   ├── Injury Engine
│   └── Exercise Database
├── Data Models
│   ├── UserProfile
│   ├── SessionState
│   ├── InjuryStatus
│   └── Exercise
└── Utilities
    ├── Health Calculator
    ├── Profile Parser
    └── Exception Handlers
```

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone <repository-url>

# Install dependencies (create requirements.txt with needed packages)
pip install -r requirements.txt
```

### Basic Usage

```python
from chatbot import HealthWellnessChatbot

# Initialize chatbot
bot = HealthWellnessChatbot()

# Process user message
user_id = "user123"
message = "I want to build muscle, I'm a beginner with access to a gym"

response = bot.process_message(user_id, message)
print(response)
```

### Command Line Interface

```bash
python chatbot.py
```

## 📚 Detailed Components

### 1. Exercise Database (`exercise_database.py`)

Comprehensive library of 100+ exercises categorized by:
- **Movement Patterns**: Squat, Hinge, Push, Pull, Core, Carry
- **Equipment**: Bodyweight, Barbell, Dumbbell, Kettlebell, Machines, Bands
- **Difficulty**: Beginner, Intermediate, Advanced
- **Muscle Groups**: Primary and secondary muscle targeting
- **Injury Contraindications**: Which injuries should avoid each exercise

```python
from exercise_database import ExerciseDatabase

# Get all squat exercises
squats = ExerciseDatabase.get_by_pattern("squat")

# Get exercises safe for knee injuries
safe_exercises = ExerciseDatabase.get_safe_for_injury("knee")

# Get beginner exercises
beginner_exercises = ExerciseDatabase.get_by_difficulty("beginner")
```

### 2. Workout Engine (`workout_engine.py`)

Generates periodized training programs with:
- **Progressive Overload**: Systematic increase in volume and intensity
- **Mesocycle Planning**: Weeks 1-4 (Foundation), 5-8 (Intensification), 9-12 (Peak)
- **Goal-Specific Programming**: Different protocols for muscle gain, fat loss, strength, endurance
- **Nutrition Calculations**: BMR, TDEE, calorie targets, macro splits

```python
from workout_engine import PlanGenerator

planner = PlanGenerator()
plan = planner.generate_multiweek_plan(user_profile, {
    "goal": "muscle gain",
    "duration_weeks": 12,
    "experience": "intermediate",
    "location": "gym",
    "time_minutes": 60
})
```

### 3. Injury Engine (`injury_engine.py`)

Smart injury classification system:

**Red Flags** (Medical referral required):
- Fractures
- Ligament ruptures (ACL, MCL)
- Dislocations
- Post-surgery complications
- Inability to bear weight

**Yellow Flags** (Modify training):
- Tendonitis/Tendinitis
- Muscle strains/sprains
- Chronic pain
- Mild inflammation

**Green** (Safe to train):
- Minor soreness
- DOMS (Delayed Onset Muscle Soreness)
- No significant issues

```python
from injury_engine import InjuryEngine

engine = InjuryEngine()
status = engine.classify("I have knee tendonitis and some pain when squatting")

print(status.region)    # "knee"
print(status.severity)  # "yellow"
```

### 4. Natural Language Understanding (`nlu.py`)

Pattern-based NLU for intent detection:

**Intents**:
- `multi_week_plan`: User wants long-term program
- `quick_session`: User wants single workout
- `injury_assistance`: User has injury concerns
- `pregnancy_modification`: User is pregnant
- `cycle_modification`: User wants cycle-aware training

**Slot Extraction**:
- Goal, duration, experience, location, time
- Injury details, body parts, pain levels
- Pregnancy trimester, weeks
- Cycle phase, day in cycle

### 5. Memory Store (`memory.py`)

Persistent user profile storage:
- JSON-based file storage
- Profile versioning and history
- Automatic backup on updates
- Injury status tracking
- Goal and preference memory

### 6. Dialog Manager (`dialog.py`)

Conversational flow management:
- Multi-turn conversations
- Context awareness
- Feature parameter collection
- Confirmation workflows
- Error recovery

## 💡 Usage Examples

### Example 1: Complete Setup

```
User: Hi, I'm a 28-year-old male, 180cm, 75kg. I want to build muscle. I'm intermediate level and have access to a gym.

Coach: Great! I can create a muscle-building program for you. A few more details:
- How many weeks would you like the program to last? (I recommend 8-12 weeks)
- How much time do you have per workout? (45-90 minutes is ideal)

User: 12 weeks, 60 minutes per session

Coach: Perfect! I'll create your 12-week muscle-building program...

[Generates comprehensive plan with nutrition and training]
```

### Example 2: Injury Management

```
User: I have knee pain from running. It hurts when I squat.

Coach: I understand you have knee pain. To help you safely:
- Where exactly is the pain? (front, side, back of knee)
- Pain level 1-10?
- Was this diagnosed by a medical professional?
- When did it start?

User: Front of knee, about a 4/10, started last week

Coach: This sounds like it could be patellar tendonitis. This is a YELLOW flag - you can train but we need to modify exercises.

I'll:
✓ Remove: Heavy squats, lunges, running, jumping
✓ Include: Romanian deadlifts, hip thrusts, upper body work
✓ Add: Knee-friendly leg exercises

Would you like me to create a modified program?
```

### Example 3: Progressive Program

```
User: I'm a complete beginner. Never worked out before. I only have dumbbells at home.

Coach: Perfect! I'll create a beginner-friendly home program with dumbbells.

Your program will focus on:
- Learning proper movement patterns
- Building base strength
- Establishing consistency
- 3 days per week, full-body workouts

The first 4 weeks focus on technique with bodyweight and light dumbbells.
Weeks 5-8 gradually increase intensity.

Sound good?

User: Yes!

Coach: [Generates beginner home program]
```

## 🎯 Goal-Specific Programming

### Fat Loss
- Caloric deficit: -500 kcal/day
- High protein: 2.0-2.5g/kg
- Higher rep ranges: 12-15 reps
- Conditioning circuits included
- 4-5 sessions per week

### Muscle Gain (Hypertrophy)
- Caloric surplus: +300-500 kcal/day
- Protein: 1.6-2.2g/kg
- Moderate reps: 8-12 reps
- Volume emphasis: 3-4 sets
- 4-5 sessions per week

### Strength
- Maintenance/slight surplus
- Lower reps: 3-6 reps
- Heavy loads: 80-95% 1RM
- Longer rest: 3-5 minutes
- Compound movements focus

### Endurance
- Maintenance/slight deficit
- Higher reps: 15-20 reps
- Lower loads: 50-65% 1RM
- Minimal rest: 30-60 seconds
- Circuit training emphasis

## 🔒 Safety & Compliance

### Medical Disclaimers
- Not a substitute for medical advice
- Serious injuries require professional evaluation
- Pregnancy training requires medical clearance
- Users assume all risk

### Red Flags Trigger Immediate Referral
- Fractures, ruptures, severe tears
- Post-surgical complications
- Inability to perform basic movements
- Severe, persistent pain
- Neurological symptoms

## 🛠️ Technical Details

### Dependencies
- Python 3.10+
- No ML dependencies in core (rule-based NLU)
- JSON for data persistence
- Regex for parsing

### Performance
- Instant response for most queries
- Profile loading: <10ms
- Plan generation: <100ms
- No external API calls required

### Scalability
- File-based storage (can migrate to DB)
- Stateless request handling
- Horizontal scaling capable
- Cacheable responses

## 📈 Future Enhancements

### Planned Features
- [ ] Video exercise demonstrations
- [ ] Progress tracking and analytics
- [ ] AI-powered form checking
- [ ] Integration with fitness trackers
- [ ] Mobile app
- [ ] Community features
- [ ] Meal planning integration
- [ ] Voice interface

### ML Enhancements
- [ ] Deep learning NLU model
- [ ] Personalized exercise recommendations
- [ ] Automated program optimization
- [ ] Predictive injury prevention
- [ ] Computer vision for form analysis

## 🤝 Contributing

Contributions welcome! Areas of focus:
1. Exercise database expansion
2. Additional injury protocols
3. Special population programs (seniors, youth)
4. Sport-specific training templates
5. Nutrition meal planning
6. Recovery protocols

## 📄 License

See LICENSE file for details.

## 📧 Support

For issues, questions, or contributions:
- Open an issue on GitHub
- Contact: [shirodkarshubham9@gmail.com]


## ⚠️ Disclaimer

This chatbot provides fitness guidance based on established exercise science principles. However:
- It is NOT a replacement for professional medical advice
- Consult a physician before starting any exercise program
- Stop exercising if you experience pain, dizziness, or discomfort
- The creators assume no liability for injuries or health issues

**Train smart. Train safe. Get strong.** 💪
