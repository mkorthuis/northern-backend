import logging
from typing import Dict, Any, Optional

from app.service.internal.llm.llm_factory import LLMFactory, LLMResponse

logger = logging.getLogger(__name__)

class JellyDonutService:
    """Service for generating jelly donut related content using LLM."""
    
    @staticmethod
    async def get_jelly_donut_response(message: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate a response from LLM using the provided message or default to "I am a jelly donut".
        
        Args:
            message: Custom message to send to the LLM. Defaults to "I am a jelly donut" if None.
            
        Returns:
            Dictionary containing the LLM response and metadata.
        """
        try:
            prompt = message if message is not None else "I am a jelly donut"
            response: LLMResponse = await LLMFactory.generate_text_async(prompt)
            
            return {
                "message": response.text,
                "model": response.model,
                "provider": response.provider,
                "prompt": prompt
            }
        except Exception as e:
            logger.error(f"Error getting jelly donut response: {str(e)}")
            raise 