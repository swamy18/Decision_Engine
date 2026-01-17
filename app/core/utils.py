import asyncio
import functools
from typing import Callable, Type, Tuple

def with_retry(
    exceptions: Tuple[Type[Exception], ...] = (Exception,), 
    retries: int = 3, 
    delay: float = 1.0, 
    backoff: float = 2.0
):
    """
    Exponential backoff retry decorator.
    """
    def decorator(func: Callable):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            current_delay = delay
            last_exception = None
            
            for attempt in range(retries):
                try:
                    return await func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt < retries - 1:
                        await asyncio.sleep(current_delay)
                        current_delay *= backoff
                    else:
                        break
            
            raise last_exception
        return wrapper
    return decorator
