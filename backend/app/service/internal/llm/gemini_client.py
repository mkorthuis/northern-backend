import os
import logging
import google.generativeai as genai
from typing import Dict, List, Optional, Union
from pydantic import BaseModel, Field
import asyncio
from functools import partial

from app.core.config import settings

# Set up logging
logger = logging.getLogger(__name__)

class GeminiConfig(BaseModel):
    """Configuration for Gemini API."""
    api_key: str = Field(..., description="Google API key for Gemini")
    model: str = Field("gemini-1.5-pro", description="Gemini model to use")
    temperature: float = Field(0.7, description="Temperature for generation")
    max_tokens: Optional[int] = Field(None, description="Maximum tokens to generate")
    top_p: Optional[float] = Field(0.95, description="Top-p value for sampling")
    top_k: Optional[int] = Field(None, description="Top-k value for sampling")

class Message(BaseModel):
    """A message in a conversation."""
    role: str = Field(..., description="Role of the message sender (user or assistant)")
    content: str = Field(..., description="Content of the message")

class GeminiResponse(BaseModel):
    """Response from Gemini API."""
    text: str = Field(..., description="Generated text response")
    usage: Dict[str, int] = Field({}, description="Token usage metrics")
    model: str = Field(..., description="Model used for generation")
    finish_reason: Optional[str] = Field(None, description="Reason for finishing generation")

class GeminiClient:
    """Client for interacting with the Gemini API."""
    
    def __init__(self, config: Optional[GeminiConfig] = None):
        """
        Initialize the Gemini client.
        
        Args:
            config: Configuration for the Gemini API. If None, will load from settings.
        """
        if config is None:
            # Use settings from config.py
            api_key = settings.GEMINI_API_KEY
            if not api_key:
                # Fall back to environment variable if not in settings
                api_key = os.getenv("GEMINI_API_KEY")
                if not api_key:
                    raise ValueError("GEMINI_API_KEY not set in settings or environment variables")
            
            self.config = GeminiConfig(
                api_key=api_key,
                model=settings.GEMINI_MODEL,
                temperature=settings.GEMINI_TEMPERATURE,
                max_tokens=settings.GEMINI_MAX_TOKENS,
                top_p=settings.GEMINI_TOP_P
            )
        else:
            self.config = config
            
        # Configure the Gemini API
        genai.configure(api_key=self.config.api_key)
        
        # Initialize the model
        self.model = genai.GenerativeModel(
            model_name=self.config.model,
            generation_config={
                "temperature": self.config.temperature,
                "top_p": self.config.top_p,
                "top_k": self.config.top_k,
                "max_output_tokens": self.config.max_tokens,
            }
        )
        
        logger.info(f"Initialized Gemini client with model {self.config.model}")
    
    def generate_text(self, prompt: str) -> GeminiResponse:
        """
        Generate text using Gemini.
        
        Args:
            prompt: The prompt for text generation.
            
        Returns:
            Generated response.
        """
        try:
            logger.debug(f"Sending prompt to Gemini: {prompt[:100]}...")
            
            response = self.model.generate_content(prompt)
            
            # Extract usage information if available
            usage = {}
            if hasattr(response, "usage_metadata"):
                usage = response.usage_metadata
            
            # Create a structured response
            result = GeminiResponse(
                text=response.text,
                usage=usage,
                model=self.config.model,
                finish_reason=getattr(response, "finish_reason", None)
            )
            
            logger.debug(f"Received response from Gemini: {result.text[:100]}...")
            return result
            
        except Exception as e:
            logger.error(f"Error generating text with Gemini: {str(e)}")
            raise
    
    def chat(self, messages: List[Message]) -> GeminiResponse:
        """
        Have a conversation with Gemini.
        
        Args:
            messages: List of message objects representing conversation history.
            
        Returns:
            Response from Gemini.
        """
        try:
            # Format messages for Gemini's chat API
            chat = self.model.start_chat(history=[])
            
            # Add each message to the chat
            for msg in messages:
                if msg.role == "user":
                    response = chat.send_message(msg.content)
                # We don't need to send assistant messages as they're part of the response
            
            # Get the last response
            last_response = response
            
            # Extract usage information if available
            usage = {}
            if hasattr(last_response, "usage_metadata"):
                usage = last_response.usage_metadata
            
            # Create a structured response
            result = GeminiResponse(
                text=last_response.text,
                usage=usage,
                model=self.config.model,
                finish_reason=getattr(last_response, "finish_reason", None)
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Error in chat with Gemini: {str(e)}")
            raise
    
    async def generate_text_async(self, prompt: str) -> GeminiResponse:
        """
        Generate text using Gemini asynchronously.
        
        Args:
            prompt: The prompt for text generation.
            
        Returns:
            Generated response.
        """
        # Use a thread pool to run the synchronous method asynchronously
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(
            None, 
            partial(self.generate_text, prompt)
        )
    
    async def chat_async(self, messages: List[Message]) -> GeminiResponse:
        """
        Have a conversation with Gemini asynchronously.
        
        Args:
            messages: List of message objects representing conversation history.
            
        Returns:
            Response from Gemini.
        """
        # Use a thread pool to run the synchronous method asynchronously
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(
            None, 
            partial(self.chat, messages)
        )

# Example usage
if __name__ == "__main__":
    # This block is for testing only
    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    
    client = GeminiClient()
    response = client.generate_text("Explain quantum computing in simple terms.")
    print(response.text)
    
    # Chat example
    messages = [
        Message(role="user", content="Hello, how are you?"),
        Message(role="assistant", content="I'm doing well, thank you for asking! How can I help you today?"),
        Message(role="user", content="Can you tell me about the solar system?")
    ]
    
    chat_response = client.chat(messages)
    print(chat_response.text) 