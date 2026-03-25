# 🚀 Complete Setup & Deployment Guide

## Quick Start (5 Minutes)

### 1. Test the Chatbot Locally

```bash
# Run the CLI version
python chatbot.py
```

That's it! Start chatting with your AI fitness coach.

---

## 📱 WhatsApp Integration Setup

### Option A: WhatsApp Web (Best for Personal Use)

**Step 1: Install Node.js**
```bash
# Download from: https://nodejs.org/
# Or use package manager:

# macOS
brew install node

# Ubuntu/Debian
sudo apt install nodejs npm

# Windows
# Download installer from nodejs.org
```

**Step 2: Install WhatsApp Library**
```bash
npm install whatsapp-web.js qrcode-terminal
```

**Step 3: Run WhatsApp Bot**
```bash
python whatsapp_integration.py
```

**Step 4: Scan QR Code**
1. Open WhatsApp on your phone
2. Go to Settings → Linked Devices
3. Tap "Link a Device"
4. Scan the QR code shown in terminal

**Step 5: Start Chatting!**
- Send messages to your WhatsApp number
- Bot responds automatically
- Works 24/7 while script is running

---

### Option B: WhatsApp Business API (For Production/Business)

**Requirements:**
- WhatsApp Business Account
- Facebook Business Manager
- Verified business

**Steps:**
1. Sign up at https://business.whatsapp.com/
2. Get API credentials
3. Use official WhatsApp Business API
4. Configure webhook for messages

**Advantages:**
- Official support
- Higher message limits
- Business features
- Better reliability

---

## 🌐 Web Interface Setup

### Streamlit (Easiest - Great UI)

```bash
# Install Streamlit
pip install streamlit

# Create app.py
```

```python
import streamlit as st
from chatbot import HealthWellnessChatbot

st.title("💪 AI Fitness Coach")

if "bot" not in st.session_state:
    st.session_state.bot = HealthWellnessChatbot()
    st.session_state.messages = []
    st.session_state.user_id = "web_user"

# Display messages
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# Chat input
if prompt := st.chat_input("Message your coach..."):
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Get bot response
    response = st.session_state.bot.process_message(
        st.session_state.user_id, 
        prompt
    )
    
    # Add bot response
    st.session_state.messages.append({"role": "assistant", "content": response})
    st.rerun()
```

```bash
# Run
streamlit run app.py
```

Opens at http://localhost:8501

---

### FastAPI (REST API - For Apps)

```bash
pip install fastapi uvicorn
```

```python
# api.py
from fastapi import FastAPI
from pydantic import BaseModel
from chatbot import HealthWellnessChatbot

app = FastAPI()
bot = HealthWellnessChatbot()

class Message(BaseModel):
    user_id: str
    text: str

@app.post("/chat")
async def chat(message: Message):
    response = bot.process_message(message.user_id, message.text)
    return {"response": response}

# Run: uvicorn api:app --reload
```

---

## 📲 Telegram Bot Setup

```bash
pip install python-telegram-bot
```

```python
# telegram_bot.py
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, CommandHandler
from chatbot import HealthWellnessChatbot

bot = HealthWellnessChatbot()

async def handle_message(update: Update, context):
    user_id = str(update.effective_user.id)
    message = update.message.text
    
    response = bot.process_message(user_id, message)
    await update.message.reply_text(response)

async def start(update: Update, context):
    await update.message.reply_text(
        "💪 Hey! I'm your AI fitness coach! Tell me your goals!"
    )

def main():
    # Get bot token from @BotFather on Telegram
    app = Application.builder().token("YOUR_BOT_TOKEN").build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT, handle_message))
    
    app.run_polling()

if __name__ == "__main__":
    main()
```

**Get Telegram Bot Token:**
1. Message @BotFather on Telegram
2. Send `/newbot`
3. Follow instructions
4. Copy token
5. Paste in code above

```bash
python telegram_bot.py
```

---

## 🚀 Production Deployment

### Heroku

```bash
# Install Heroku CLI
# Create Procfile
echo "web: python chatbot.py" > Procfile

# Create runtime.txt
echo "python-3.10.0" > runtime.txt

# Deploy
heroku login
heroku create your-fitness-bot
git push heroku main
```

### AWS EC2

```bash
# Connect to instance
ssh -i key.pem ubuntu@your-instance

# Install dependencies
sudo apt update
sudo apt install python3-pip nodejs npm

# Clone repo
git clone your-repo
cd your-repo

# Install requirements
pip3 install -r requirements.txt

# Run with screen (keeps running after disconnect)
screen -S fitness-bot
python3 chatbot.py

# Detach: Ctrl+A, then D
# Reattach: screen -r fitness-bot
```

### Docker

```dockerfile
# Dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "chatbot.py"]
```

```bash
# Build and run
docker build -t fitness-bot .
docker run -d --name fitness-bot fitness-bot
```

---

## 🔧 Configuration

### Environment Variables

Create `.env` file:

```env
# WhatsApp
WHATSAPP_SESSION_PATH=./whatsapp_session

# Database (optional)
DATABASE_URL=sqlite:///fitness_bot.db

# API Keys (if needed)
TELEGRAM_BOT_TOKEN=your_token_here
WHATSAPP_API_KEY=your_key_here

# Settings
PROFILES_DIR=./profiles
DEBUG=False
```

### Load in Python:

```python
from dotenv import load_dotenv
import os

load_dotenv()

TELEGRAM_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
```

---

## 📊 Monitoring & Logs

### Simple Logging

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)
logger.info("Bot started")
```

---

## 🔒 Security Best Practices

1. **Never commit sensitive data**
   ```bash
   # Add to .gitignore
   .env
   whatsapp_session/
   profiles/
   *.log
   ```

2. **Use environment variables**
   - API keys
   - Database credentials
   - Tokens

3. **Rate limiting**
   ```python
   from time import time, sleep
   
   last_message = {}
   
   def rate_limit(user_id, seconds=2):
       now = time()
       if user_id in last_message:
           if now - last_message[user_id] < seconds:
               sleep(seconds - (now - last_message[user_id]))
       last_message[user_id] = now
   ```

4. **Input validation**
   - Already handled in code
   - Sanitize user inputs
   - Prevent injection attacks

---

## 🧪 Testing

```bash
# Run tests
pytest tests/

# With coverage
pytest --cov=. tests/
```

---

## 📈 Scaling

### For High Traffic:

1. **Database**: Migrate from JSON to PostgreSQL
2. **Queue**: Use Celery for async processing
3. **Cache**: Redis for session management
4. **Load Balancer**: Multiple bot instances

---

## 🆘 Troubleshooting

### WhatsApp QR code not showing
```bash
# Check Node.js installed
node --version

# Reinstall packages
npm install whatsapp-web.js qrcode-terminal --force
```

### Bot not responding
```bash
# Check logs
tail -f bot.log

# Restart bot
pkill -f chatbot.py
python chatbot.py
```

### Permission errors
```bash
# Fix permissions
chmod +x chatbot.py
chmod -R 755 profiles/
```

---

## 📞 Support

- **Issues**: Create GitHub issue
- **Questions**: Check README.md
- **Contributions**: Pull requests welcome!

---

## 🎯 Platform Comparison

| Platform | Difficulty | Users | Best For |
|----------|-----------|-------|----------|
| CLI | ⭐ Easy | You | Testing |
| Streamlit | ⭐⭐ Easy | Web | Demos |
| WhatsApp | ⭐⭐⭐ Medium | Mobile | Personal |
| Telegram | ⭐⭐ Easy | Mobile | Community |
| API | ⭐⭐⭐ Medium | Apps | Integration |
| Business API | ⭐⭐⭐⭐ Hard | Business | Production |

---

## ✅ Launch Checklist

- [ ] Test chatbot locally
- [ ] Choose platform (WhatsApp/Telegram/Web)
- [ ] Install dependencies
- [ ] Configure environment variables
- [ ] Test with real users
- [ ] Set up monitoring
- [ ] Deploy to production
- [ ] Document for users
- [ ] Set up backup strategy
- [ ] Plan scaling approach

---

**🎉 You're Ready to Launch!**

Choose your platform and follow the steps above. Your AI fitness coach will be helping people in minutes!
