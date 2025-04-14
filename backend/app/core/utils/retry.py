import asyncio
import logging
from typing import TypeVar, Callable, Optional
from functools import wraps

logger = logging.getLogger(__name__)

T = TypeVar('T')

async def retry_with_exponential_backoff(
    func: Callable[..., T],
    max_retries: int = 3,
    initial_delay: int = 3,
    max_delay: int = 60,
    exponential_base: int = 2,
    logger: Optional[logging.Logger] = None
) -> T:
    """
    Retries an async function with exponential backoff.
    
    Args:
        func: The async function to retry
        max_retries: Maximum number of retry attempts
        initial_delay: Initial delay between retries in seconds
        max_delay: Maximum delay between retries in seconds
        exponential_base: Base for exponential backoff calculation
        logger: Optional logger instance for logging retries
    
    Returns:
        The result of the async function
    """
    for attempt in range(max_retries):
        try:
            return await func()
        except Exception as e:
            if attempt == max_retries - 1:
                raise
            
            delay = min(initial_delay * (exponential_base ** attempt), max_delay)
            error_msg = f"Attempt {attempt + 1} failed, retrying in {delay} seconds... Error: {str(e)}"
            
            if logger:
                logger.warning(error_msg)
            else:
                print(error_msg)
                
            await asyncio.sleep(delay)

def with_retry(
    max_retries: int = 3,
    initial_delay: int = 3,
    max_delay: int = 60,
    exponential_base: int = 2
):
    """
    Decorator that adds retry functionality to an async function.
    
    Args:
        max_retries: Maximum number of retry attempts
        initial_delay: Initial delay between retries in seconds
        max_delay: Maximum delay between retries in seconds
        exponential_base: Base for exponential backoff calculation
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            async def _make_request():
                return await func(*args, **kwargs)
            return await retry_with_exponential_backoff(
                _make_request,
                max_retries=max_retries,
                initial_delay=initial_delay,
                max_delay=max_delay,
                exponential_base=exponential_base,
                logger=logger
            )
        return wrapper
    return decorator 