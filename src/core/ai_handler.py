"""
AI Language Model Handler for Terry the Tube
"""
from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
import sys
import os
import time
import logging
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from config import OLLAMA_MODEL, OLLAMA_TEMPERATURE, OLLAMA_TIMEOUT, DEFAULT_PERSONALITY
from src.personalities import get_personality_by_key

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AIHandler:
    def __init__(self, personality_key=None):
        """Initialize the AI language model handler with specified personality"""
        try:
            self.model = OllamaLLM(
                model=OLLAMA_MODEL, 
                temperature=OLLAMA_TEMPERATURE, 
                timeout=OLLAMA_TIMEOUT
            )
            
            # Set personality
            self.personality_key = personality_key or DEFAULT_PERSONALITY
            self.personality_config = get_personality_by_key(self.personality_key)
            if not self.personality_config:
                raise ValueError(f"Unknown personality: {self.personality_key}")
            
            self.prompt = ChatPromptTemplate.from_template(self.personality_config["prompt_template"])
            self.chain = self.prompt | self.model
            
            print(f"AI Handler initialized with model: {OLLAMA_MODEL}")
            print(f"Personality: {self.personality_config['name']}")
        except Exception as e:
            print(f"Error initializing LLM: {e}")
            print("Please make sure Ollama is running and the model is available")
            raise
    
    def generate_response(self, conversation_history, question_count=1):
        """Generate AI response based on conversation history and question count"""
        context = "\n".join(conversation_history)
        # Add question count information to context
        context += f"\n\nCURRENT QUESTION NUMBER: {question_count} (out of 3 maximum)"
        if question_count >= 3:
            context += "\nYou've already asked 3 questions."
        
        logger.info(f"Starting LLM generation for question {question_count}")
        start_time = time.time()
        
        try:
            response = self.chain.invoke({"context": context})
            
            generation_time = time.time() - start_time
            logger.info(f"LLM generation completed in {generation_time:.2f} seconds for question {question_count}")
            
            return response.strip()
        except Exception as e:
            generation_time = time.time() - start_time
            print(f"Error generating response: {e}")
            logger.error(f"LLM generation failed after {generation_time:.2f} seconds: {e}")
            raise
    
    def is_model_available(self):
        """Check if the AI model is available and responsive"""
        logger.info("Starting LLM availability check")
        start_time = time.time()
        
        try:
            test_response = self.chain.invoke({"context": "Test message"})
            
            check_time = time.time() - start_time
            logger.info(f"LLM availability check completed in {check_time:.2f} seconds - Model is available")
            
            return True
        except Exception as e:
            check_time = time.time() - start_time
            logger.warning(f"LLM availability check failed after {check_time:.2f} seconds: {e}")
            return False
    
    def get_personality_info(self):
        """Get current personality information"""
        return {
            "key": self.personality_key,
            "name": self.personality_config["name"],
            "short_name": self.personality_config["short_name"]
        }
    
    def get_greeting_message(self):
        """Get personality-specific greeting message"""
        return self.personality_config["greeting"]
    
    def get_exit_string(self):
        """Get personality-specific exit string"""
        return self.personality_config["exit_string"]