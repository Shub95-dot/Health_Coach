import ollama
import os
from typing import List, Dict, Optional
from dotenv import load_dotenv

load_dotenv()

class OllamaEngine:
    """
    Handles interactions with local Ollama LLM
    """
    
    def __init__(self, model: Optional[str] = None):
        self.model = model or os.getenv("OLLAMA_MODEL", "llama3")
        
    def generate_response(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """
        Generate a response from the LLM
        """
        messages = []
        if system_prompt:
            messages.append({'role': 'system', 'content': system_prompt})
        
        messages.append({'role': 'user', 'content': prompt})
        
        try:
            response = ollama.chat(model=self.model, messages=messages)
            return response['message']['content']
        except Exception as e:
            return f"Error connecting to Ollama: {str(e)}. Make sure Ollama is running locally."

    def chat(self, messages: List[Dict[str, str]]) -> str:
        """
        Handle a multi-turn conversation
        """
        try:
            response = ollama.chat(model=self.model, messages=messages)
            return response['message']['content']
        except Exception as e:
            return f"Error connecting to Ollama: {str(e)}"
