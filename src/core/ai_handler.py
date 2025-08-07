"""
AI Language Model Handler for Terry the Tube
"""
from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from config import OLLAMA_MODEL, OLLAMA_TEMPERATURE, OLLAMA_TIMEOUT, AI_PERSONALITY_TEMPLATE


class AIHandler:
    def __init__(self):
        """Initialize the AI language model handler"""
        try:
            self.model = OllamaLLM(
                model=OLLAMA_MODEL, 
                temperature=OLLAMA_TEMPERATURE, 
                timeout=OLLAMA_TIMEOUT
            )
            self.prompt = ChatPromptTemplate.from_template(AI_PERSONALITY_TEMPLATE)
            self.chain = self.prompt | self.model
            print(f"AI Handler initialized with model: {OLLAMA_MODEL}")
        except Exception as e:
            print(f"Error initializing LLM: {e}")
            print("Please make sure Ollama is running and the model is available")
            raise
    
    def generate_response(self, conversation_history):
        """Generate AI response based on conversation history"""
        try:
            context = "\n".join(conversation_history)
            response = self.chain.invoke({"context": context})
            return response.strip()
        except Exception as e:
            print(f"Error generating response: {e}")
            raise
    
    def is_model_available(self):
        """Check if the AI model is available and responsive"""
        try:
            test_response = self.chain.invoke({"context": "Test message"})
            return True
        except Exception:
            return False