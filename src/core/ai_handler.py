"""
AI Language Model Handler for Terry the Tube
Supports both OpenAI GPT and Ollama models
"""
from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
import sys
import os
import time
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from config import (
    USE_OPENAI_CHAT, OLLAMA_MODEL, OLLAMA_TEMPERATURE, OLLAMA_TIMEOUT, DEFAULT_PERSONALITY
)
from src.personalities import get_personality_by_key
from src.audio.openai_chat_client import OpenAIChatClient


class AIHandler:
    def __init__(self, personality_key=None):
        try:
            # Set personality first
            self.personality_key = personality_key or DEFAULT_PERSONALITY
            self.personality_config = get_personality_by_key(self.personality_key)
            if not self.personality_config:
                raise ValueError(f"Unknown personality: {self.personality_key}")
        
            # Initialize AI clients
            self.use_openai = USE_OPENAI_CHAT
            self.openai_client = None
            self.ollama_model = None
            self.ollama_chain = None
            self.last_generation_time = 0.0
            
            if self.use_openai:
                try:
                    self.openai_client = OpenAIChatClient()
                    if self.openai_client.is_available():
                        print(f"AI Handler initialized with OpenAI Chat")
                    else:
                        print("OpenAI Chat not available, falling back to Ollama")
                        self.use_openai = False
                except Exception as e:
                    print(f"Failed to initialize OpenAI Chat: {e}")
                    print("Falling back to Ollama")
                    self.use_openai = False
            
            # Initialize Ollama as fallback or primary
            if not self.use_openai or not (self.openai_client and self.openai_client.is_available()):
                self.ollama_model = OllamaLLM(
                    model=OLLAMA_MODEL, 
                    temperature=OLLAMA_TEMPERATURE, 
                    timeout=OLLAMA_TIMEOUT
                )
                self.prompt = ChatPromptTemplate.from_template(self.personality_config["prompt_template"])
                self.ollama_chain = self.prompt | self.ollama_model
                print(f"AI Handler initialized with Ollama model: {OLLAMA_MODEL}")
            
            print(f"Personality: {self.personality_config['name']}")
        except Exception as e:
            print(f"Error initializing AI Handler: {e}")
            if not self.use_openai:
                print("Please make sure Ollama is running and the model is available")
            raise
    
    def generate_response(self, conversation_history, question_count=1):
        try:
            start_time = time.time()
            
            # Prepare context with question count information
            context = "\n".join(conversation_history)
            context += f"\n\nCURRENT QUESTION NUMBER: {question_count} (out of 3 maximum)"
            if question_count >= 3:
                context += "\nYou've already asked 3 questions."
            
            # Use OpenAI if available and enabled
            if self.use_openai and self.openai_client and self.openai_client.is_available():
                system_prompt = self.personality_config["prompt_template"].replace("{context}", "")
                response, _ = self.openai_client.generate_response(
                    system_prompt=system_prompt,
                    user_message=context
                )
                self.last_generation_time = time.time() - start_time
                print(f"Response generated in {self.last_generation_time:.2f}s")
                return response.strip()
            
            # Fall back to Ollama
            elif self.ollama_chain:
                response = self.ollama_chain.invoke({"context": context})
                self.last_generation_time = time.time() - start_time
                print(f"Response generated in {self.last_generation_time:.2f}s")
                return response.strip()
            
            else:
                raise Exception("No AI model available")
                
        except Exception as e:
            print(f"Error generating response: {e}")
            raise
    
    def get_last_generation_time(self):
        """Get the time it took to generate the last response"""
        return self.last_generation_time
    
    def is_model_available(self):
        try:
            if self.use_openai and self.openai_client and self.openai_client.is_available():
                return self.openai_client.test_connection()
            elif self.ollama_chain:
                test_response = self.ollama_chain.invoke({"context": "Test message"})
                return True
            return False
        except Exception:
            return False
    
    def get_personality_info(self):
        return {
            "key": self.personality_key,
            "name": self.personality_config["name"],
            "short_name": self.personality_config["short_name"]
        }
    
    def get_greeting_message(self):
        return self.personality_config["greeting"]
    
    def get_exit_string(self):
        return self.personality_config["exit_string"]