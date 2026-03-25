"""
WhatsApp Web Integration for Health & Fitness Chatbot
Uses whatsapp-web.js for WhatsApp connectivity
"""

# NOTE: This is a Python wrapper that will work with Node.js whatsapp-web.js
# You need to install: npm install whatsapp-web.js qrcode-terminal

import json
import subprocess
import os
from typing import Optional, Callable


class WhatsAppBot:
    """
    WhatsApp integration for the fitness chatbot
    Handles message sending/receiving via WhatsApp Web
    """
    
    def __init__(self, chatbot_instance, session_path: str = "./whatsapp_session"):
        """
        Initialize WhatsApp bot
        
        Args:
            chatbot_instance: Instance of HealthWellnessChatbot
            session_path: Path to store WhatsApp session data
        """
        self.chatbot = chatbot_instance
        self.session_path = session_path
        self.node_script_path = self._create_node_script()
    
    def _create_node_script(self) -> str:
        """Create the Node.js script for WhatsApp integration"""
        
        script_content = '''
const { Client, LocalAuth } = require('whatsapp-web.js');
const qrcode = require('qrcode-terminal');
const fs = require('fs');

const client = new Client({
    authStrategy: new LocalAuth({
        dataPath: './whatsapp_session'
    })
});

client.on('qr', (qr) => {
    console.log('WHATSAPP_QR_CODE:');
    qrcode.generate(qr, {small: true});
});

client.on('ready', () => {
    console.log('WHATSAPP_READY');
});

client.on('message', async (message) => {
    // Send message data to Python via file
    const messageData = {
        from: message.from,
        body: message.body,
        timestamp: Date.now()
    };
    
    // Write to tmp then rename for atomicity
    const tmpIncoming = 'whatsapp_incoming.json.tmp';
    fs.writeFileSync(tmpIncoming, JSON.stringify(messageData));
    fs.renameSync(tmpIncoming, 'whatsapp_incoming.json');
    
    // Wait for response from Python
    let response = '';
    let attempts = 0;
    while (!response && attempts < 200) { // Increased timeout to 20s
        if (fs.existsSync('whatsapp_outgoing.json')) {
            try {
                response = fs.readFileSync('whatsapp_outgoing.json', 'utf8');
                fs.unlinkSync('whatsapp_outgoing.json');
                break;
            } catch (err) {
                // File might be locked or incomplete
                await new Promise(resolve => setTimeout(resolve, 50));
            }
        }
        await new Promise(resolve => setTimeout(resolve, 100));
        attempts++;
    }
    
    if (response) {
        const responseData = JSON.parse(response);
        
        // Split long messages for WhatsApp
        const chunks = responseData.text.match(/[\\s\\S]{1,4000}/g) || [];
        
        for (const chunk of chunks) {
            await message.reply(chunk);
            await new Promise(resolve => setTimeout(resolve, 500));
        }
    }
});

client.initialize();

// Keep alive
process.on('SIGINT', () => {
    console.log('Shutting down...');
    client.destroy();
    process.exit();
});
'''
        
        script_path = "whatsapp_bot.js"
        with open(script_path, 'w') as f:
            f.write(script_content)
        
        return script_path
    
    def start(self):
        """Start the WhatsApp bot"""
        print("Starting WhatsApp Bot...")
        print("Scan the QR code with your WhatsApp mobile app")
        print("-" * 50)
        
        # Start Node.js process
        self.node_process = subprocess.Popen(
            ['node', self.node_script_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True
        )
        
        # Monitor for messages
        self._monitor_messages()
    
    def _monitor_messages(self):
        """Monitor for incoming messages and respond"""
        import time
        
        print("Bot is ready! Monitoring for messages...")
        
        while True:
            # Check for incoming message
            if os.path.exists('whatsapp_incoming.json'):
                try:
                    with open('whatsapp_incoming.json', 'r') as f:
                        message_data = json.load(f)
                    
                    # Delete the file
                    os.remove('whatsapp_incoming.json')
                    
                    # Process with chatbot
                    user_id = message_data['from']
                    user_message = message_data['body']
                    
                    print(f"\nReceived from {user_id}: {user_message}")
                    
                    # Get response from chatbot
                    response = self.chatbot.process_message(user_id, user_message)
                    
                    print(f"Responding: {response[:100]}...")
                    
                    # Write response
                    with open('whatsapp_outgoing.json', 'w') as f:
                        json.dump({"text": response}, f)
                
                except Exception as e:
                    print(f"Error processing message: {e}")
            
            time.sleep(0.1)  # Check every 100ms


# Simpler Python-only WhatsApp integration using pywhatkit
class SimpleWhatsAppBot:
    """
    Simplified WhatsApp integration using pywhatkit
    Good for testing and simple use cases
    """
    
    def __init__(self, chatbot_instance):
        self.chatbot = chatbot_instance
        
        try:
            import pywhatkit
            self.whatsapp = pywhatkit
        except ImportError:
            print("Please install: pip install pywhatkit")
            self.whatsapp = None
    
    def send_message(self, phone_number: str, message: str):
        """
        Send message via WhatsApp
        
        Args:
            phone_number: Phone number with country code (e.g., +1234567890)
            message: Message to send
        """
        if not self.whatsapp:
            print("pywhatkit not installed!")
            return
        
        # Send message immediately
        import datetime
        now = datetime.datetime.now()
        hour = now.hour
        minute = now.minute + 2  # Send 2 minutes from now
        
        self.whatsapp.sendwhatmsg(phone_number, message, hour, minute)


# Installation instructions
def print_whatsapp_setup_instructions():
    """Print setup instructions for WhatsApp integration"""
    
    instructions = """
    ╔════════════════════════════════════════════════════════════════╗
    ║         WhatsApp Integration Setup Instructions                ║
    ╚════════════════════════════════════════════════════════════════╝
    
    OPTION 1: Full Integration (whatsapp-web.js) - RECOMMENDED
    ───────────────────────────────────────────────────────────────
    
    1. Install Node.js (if not installed):
       https://nodejs.org/
    
    2. Install required packages:
       npm install whatsapp-web.js qrcode-terminal
    
    3. Run the bot:
       python whatsapp_integration.py
    
    4. Scan QR code with WhatsApp on your phone:
       WhatsApp → Settings → Linked Devices → Link a Device
    
    5. Start chatting! Messages will be processed automatically
    
    
    OPTION 2: Simple Integration (pywhatkit) - For Testing
    ───────────────────────────────────────────────────────────────
    
    1. Install package:
       pip install pywhatkit
    
    2. This opens WhatsApp Web in browser and sends messages
       Good for testing but requires manual intervention
    
    
    OPTION 3: Business API (For Production)
    ───────────────────────────────────────────────────────────────
    
    1. Sign up for WhatsApp Business API:
       https://business.whatsapp.com/
    
    2. Get API credentials
    
    3. Use official WhatsApp Business API SDK
    
    
    FILE STRUCTURE:
    ───────────────────────────────────────────────────────────────
    your_project/
    ├── chatbot.py              # Main chatbot
    ├── whatsapp_integration.py # This file
    ├── whatsapp_bot.js        # Auto-generated Node.js script
    └── whatsapp_session/      # Session data (auto-created)
    
    
    SECURITY NOTES:
    ───────────────────────────────────────────────────────────────
    - Keep session data secure
    - Don't commit whatsapp_session/ to git
    - Use environment variables for sensitive data
    - Rate limit messages to avoid bans
    
    ════════════════════════════════════════════════════════════════
    """
    
    print(instructions)


if __name__ == "__main__":
    print_whatsapp_setup_instructions()
    
    print("\nStarting WhatsApp Bot Setup...")
    print("=" * 60)
    
    # Example usage
    from chatbot import HealthWellnessChatbot
    
    # Initialize chatbot
    chatbot = HealthWellnessChatbot()
    
    # Create WhatsApp bot
    whatsapp_bot = WhatsAppBot(chatbot)
    
    # Start (this will show QR code)
    try:
        whatsapp_bot.start()
    except KeyboardInterrupt:
        print("\n\nShutting down gracefully...")
        print("Goodbye! 👋")
