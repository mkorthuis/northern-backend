import logging
from typing import Optional, List, Dict, Any, Union
from pydantic import BaseModel

from app.core.config import settings
from app.service.internal.llm.gemini_client import GeminiClient, Message as GeminiMessage, GeminiResponse

# Set up logging
logger = logging.getLogger(__name__)

class Message(BaseModel):
    """A unified message model for all LLM providers."""
    role: str
    content: str

class LLMResponse(BaseModel):
    """A unified response model for all LLM providers."""
    text: str
    usage: Dict[str, Any] = {}
    model: str
    provider: str
    finish_reason: Optional[str] = None
    raw_response: Optional[Any] = None

class LLMFactory:
    """Factory for creating LLM clients based on configuration."""
    
    _gemini_client: Optional[GeminiClient] = None
    
    @classmethod
    def get_client(cls) -> GeminiClient:
        """
        Get the Gemini client instance.
        
        Returns:
            A GeminiClient instance.
        """
        if cls._gemini_client is None:
            cls._gemini_client = GeminiClient()
        return cls._gemini_client
    
    @classmethod
    def generate_text(cls, prompt: str) -> LLMResponse:
        """
        Generate text using Gemini.
        
        Args:
            prompt: The prompt for text generation.
            
        Returns:
            Generated response in a unified format.
        """
        client = cls.get_client()
        
        try:
            response = client.generate_text(prompt)
            return LLMResponse(
                text=response.text,
                usage=response.usage,
                model=response.model,
                provider="gemini",
                finish_reason=response.finish_reason,
                raw_response=response
            )
                
        except Exception as e:
            logger.error(f"Error generating text with Gemini: {str(e)}")
            raise
    
    @classmethod
    def chat(cls, messages: List[Message]) -> LLMResponse:
        """
        Have a conversation using Gemini.
        
        Args:
            messages: List of message objects representing conversation history.
            
        Returns:
            Response in a unified format.
        """
        client = cls.get_client()
        
        try:
            # Convert messages to Gemini format
            gemini_messages = [
                GeminiMessage(role=msg.role, content=msg.content) 
                for msg in messages
            ]
            
            response = client.chat(gemini_messages)
            return LLMResponse(
                text=response.text,
                usage=response.usage,
                model=response.model,
                provider="gemini",
                finish_reason=response.finish_reason,
                raw_response=response
            )
                
        except Exception as e:
            logger.error(f"Error in chat with Gemini: {str(e)}")
            raise
    
    @classmethod
    async def generate_text_async(cls, prompt: str) -> LLMResponse:
        """
        Generate text asynchronously using Gemini.
        
        Args:
            prompt: The prompt for text generation.
            
        Returns:
            Generated response in a unified format.
        """
        client = cls.get_client()
        
        try:
            response = await client.generate_text_async(prompt)
            return LLMResponse(
                text=response.text,
                usage=response.usage,
                model=response.model,
                provider="gemini",
                finish_reason=response.finish_reason,
                raw_response=response
            )
                
        except Exception as e:
            logger.error(f"Error generating text asynchronously with Gemini: {str(e)}")
            raise
    
    @classmethod
    async def chat_async(cls, messages: List[Message]) -> LLMResponse:
        """
        Have a conversation asynchronously using Gemini.
        
        Args:
            messages: List of message objects representing conversation history.
            
        Returns:
            Response in a unified format.
        """
        client = cls.get_client()
        
        try:
            # Convert messages to Gemini format
            gemini_messages = [
                GeminiMessage(role=msg.role, content=msg.content) 
                for msg in messages
            ]
            
            response = await client.chat_async(gemini_messages)
            return LLMResponse(
                text=response.text,
                usage=response.usage,
                model=response.model,
                provider="gemini",
                finish_reason=response.finish_reason,
                raw_response=response
            )
                
        except Exception as e:
            logger.error(f"Error in chat asynchronously with Gemini: {str(e)}")
            raise 