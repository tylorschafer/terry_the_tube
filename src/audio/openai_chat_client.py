import os
import sys
import time
from typing import Optional

# Add project root to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None
    print("Warning: openai package not installed. Run: pip install openai")

from config import (
    USE_OPENAI_CHAT, OPENAI_CHAT_MODEL,
    OPENAI_CHAT_TIMEOUT
)


class OpenAIChatClient:
    def __init__(self):
        self.client = None
        self.available = False

        # Check if OpenAI is available and configured
        if OpenAI is None:
            print("OpenAI package not installed")
            return

        if not USE_OPENAI_CHAT:
            print("OpenAI Chat disabled in configuration")
            return

        # Initialize OpenAI client
        try:
            self.client = OpenAI()  # Uses OPENAI_API_KEY environment variable
            self.available = True
            print(f"OpenAI Chat initialized with model: {OPENAI_CHAT_MODEL}")
        except Exception as e:
            print(f"Failed to initialize OpenAI Chat: {e}")
            print("Make sure OPENAI_API_KEY environment variable is set")

    def is_available(self) -> bool:
        return self.available and self.client is not None

    def generate_response(self, system_prompt: str, user_message: str, conversation_history: list = None) -> tuple[str, float]:
        """
        Generate a chat response using OpenAI GPT
        Returns (response_text, generation_time_seconds)
        """
        if not self.is_available():
            raise Exception("OpenAI Chat not available")

        start_time = time.time()

        try:
            # Build messages array
            messages = [{"role": "system", "content": system_prompt}]

            # Add conversation history if provided
            if conversation_history:
                messages.extend(conversation_history)

            # Add current user message
            messages.append({"role": "user", "content": user_message})

            print(f"Generating response with OpenAI {OPENAI_CHAT_MODEL}...")

            # Call OpenAI Chat API
            response = self.client.chat.completions.create(
                model=OPENAI_CHAT_MODEL,
                messages=messages,
                timeout=OPENAI_CHAT_TIMEOUT
            )

            generation_time = time.time() - start_time
            response_text = response.choices[0].message.content

            print(f"OpenAI response generated in {generation_time:.2f}s")
            return response_text, generation_time

        except Exception as e:
            print(f"OpenAI Chat generation failed: {e}")
            raise

    def get_available_models(self) -> list:
        return ["gpt-4o-mini", "gpt-4o", "gpt-4-turbo", "gpt-3.5-turbo"]

    def test_connection(self) -> bool:
        """Test if OpenAI API is accessible"""
        if not self.is_available():
            return False

        try:
            # Test with a simple prompt
            response, _ = self.generate_response(
                "You are a helpful assistant.",
                "Say hello."
            )
            return bool(response)
        except Exception as e:
            print(f"OpenAI Chat test failed: {e}")
            return False

    def get_system_info(self) -> dict:
        return {
            "openai_chat_available": self.is_available(),
            "model": OPENAI_CHAT_MODEL if self.is_available() else "N/A",
            "temperature": 0.7 if self.is_available() else "N/A",
            "timeout": OPENAI_CHAT_TIMEOUT if self.is_available() else "N/A",
            "api_key_set": bool(os.getenv("OPENAI_API_KEY")),
            "use_openai_chat": USE_OPENAI_CHAT
        }
