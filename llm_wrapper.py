# LLM choices
from openai import OpenAI
from anthropic import Anthropic
from llamaapi import LlamaAPI
import google.generativeai as genai

# Configuration
from config import Config
# Token Usage class
from structures import TokenUsage
from typing import Tuple, Optional
# Rate Limiting Logic
import time
from datetime import datetime, timedelta
from collections import deque
import threading
import logging
import os
# Sets up logging
log_directory = 'logs'
if not os.path.exists(log_directory):
    os.makedirs(log_directory)
    
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
log_file = os.path.join(log_directory, "llm_wrapper.log")
handler = logging.FileHandler(log_file)
formatter = logging.Formatter("%(asctime)s -  %(levelname)s - %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)

config = Config()

class APICallRetrier:
    """Handles retries for API calls with exponential backoff"""
    def __init__(self, max_retries: int = 3, base_delay: float = 1.0):
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.logger = logger

    def execute(self, func, *args, **kwargs):
        """Execute an API call with retries"""
        last_exception = None
        
        for attempt in range(self.max_retries):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                last_exception = e
                
                # Don't retry on authentication or validation errors
                if hasattr(e, 'status_code') and e.status_code in [400, 401, 403]:
                    raise
                
                # Calculate delay with exponential backoff
                delay = self.base_delay * (2 ** attempt)
                
                self.logger.warning(
                    f"API call failed (attempt {attempt + 1}/{self.max_retries}): {str(e)}. "
                    f"Retrying in {delay} seconds..."
                )
                
                time.sleep(delay)
        
        # If we've exhausted all retries, raise the last exception
        self.logger.error(f"API call failed after {self.max_retries} attempts: {str(last_exception)}")
        raise last_exception

class TokenRateLimiter:
    """Thread-safe token rate limiter with rolling window"""
    def __init__(self, tokens_per_minute: int = 80000, lock_timeout: float = 5.0):
        self.tokens_per_minute = tokens_per_minute
        self.usage_history = deque()  # [(timestamp, TokenUsage)]
        self.lock = threading.RLock()  # Using RLock instead of Lock
        self.logger = logger
        self.lock_timeout = lock_timeout
        self._current_usage = 0
        self._last_cleanup = datetime.now()
        
    def _try_acquire_lock(self, operation_name: str) -> bool:
        """Try to acquire lock with logging"""
        acquired = self.lock.acquire(timeout=self.lock_timeout)
        if not acquired:
            self.logger.warning(
                f"Lock timeout in {operation_name}. "
                f"Current usage: {self._current_usage}, "
                f"Queue size: {len(self.usage_history)}"
            )
        return acquired
    
    def _clean_expired_usage(self) -> None:
        """Remove individual requests older than 1 minute and update current usage"""
        now = datetime.now()
        
        # Only clean if at least 5 seconds have passed since last cleanup
        if (now - self._last_cleanup).total_seconds() < 5:
            return
            
        tokens_removed = 0
        while self.usage_history:
            timestamp, usage = self.usage_history[0]
            if now - timestamp > timedelta(minutes=1):
                self.usage_history.popleft()
                tokens_removed += usage.total_tokens
            else:
                break
                
        if tokens_removed > 0:
            self._current_usage = max(0, self._current_usage - tokens_removed)
            self.logger.info(f"Removed {tokens_removed} expired tokens. New usage: {self._current_usage}")
            
        self._last_cleanup = now
    
    def get_current_usage(self) -> int:
        """Get total token usage for the current rolling window"""
        try:
            if self._try_acquire_lock("get_current_usage"):
                try:
                    self._clean_expired_usage()
                    return self._current_usage
                finally:
                    self.lock.release()
            return self._current_usage  # Return current value if lock fails
        except Exception as e:
            self.logger.error(f"Error in get_current_usage: {e}")
            return self._current_usage
    
    def get_available_tokens(self) -> int:
        """Get number of tokens still available in current window"""
        current_usage = self.get_current_usage()
        available = self.tokens_per_minute - current_usage
        self.logger.debug(f"Current usage: {current_usage}, Available tokens: {available}")
        return available
    
    def record_usage(self, usage: TokenUsage):
        """Record token usage from an API call"""
        try:
            if self._try_acquire_lock("record_usage"):
                try:
                    now = datetime.now()
                    self._clean_expired_usage()
                    
                    self.usage_history.append((now, usage))
                    self._current_usage += usage.total_tokens
                    
                    self.logger.info(
                        f"Recorded usage - New request: {usage.total_tokens}, "
                        f"Total current usage: {self._current_usage}, "
                        f"Available: {self.tokens_per_minute - self._current_usage}, "
                        f"Active requests: {len(self.usage_history)}"
                    )
                finally:
                    self.lock.release()
            else:
                # Update usage count even if we couldn't acquire the lock
                self._current_usage += usage.total_tokens
                self.logger.warning("Updating usage without lock due to timeout")
        except Exception as e:
            self.logger.error(f"Error in record_usage: {e}")
    
    def wait_if_needed(self, estimated_tokens: int):
        """
        Wait if necessary to stay within rate limits with dynamic wait times.
        Uses exponential backoff for lock acquisition attempts.
        """
        max_attempts = 5
        base_wait = 0.1
        
        for attempt in range(max_attempts):
            lock_acquired = False
            try:
                lock_acquired = self._try_acquire_lock("wait_if_needed")
                if lock_acquired:
                    self._clean_expired_usage()
                    available_tokens = self.tokens_per_minute - self._current_usage
                    
                    if available_tokens >= estimated_tokens:
                        self.lock.release()
                        return
                    
                    if not self.usage_history:
                        self.lock.release()
                        time.sleep(0.1)
                        continue
                    
                    # Calculate how many tokens we need to free up
                    tokens_needed = estimated_tokens - available_tokens
                    tokens_to_free = 0
                    wait_until = None
                    
                    for timestamp, usage in self.usage_history:
                        tokens_to_free += usage.total_tokens
                        if tokens_to_free >= tokens_needed:
                            wait_until = timestamp + timedelta(minutes=1)
                            break
                    
                    if wait_until is None:
                        wait_until = self.usage_history[0][0] + timedelta(minutes=1)
                    
                    wait_time = (wait_until - datetime.now()).total_seconds()
                    
                    if wait_time > 0:
                        self.logger.info(
                            f"Waiting {wait_time:.2f}s for tokens. "
                            f"Current usage: {self._current_usage}, "
                            f"Available: {available_tokens}, "
                            f"Needed: {estimated_tokens}, "
                            f"Tokens to free: {tokens_to_free}"
                        )
                        self.lock.release()
                        time.sleep(min(wait_time + 0.1, 1.0))
                else:
                    # Use exponential backoff when lock acquisition fails
                    backoff_time = base_wait * (2 ** attempt)
                    self.logger.info(f"Lock acquisition failed, waiting {backoff_time:.2f}s before retry")
                    time.sleep(backoff_time)
                    
            except Exception as e:
                self.logger.error(f"Error in wait_if_needed: {e}")
                if lock_acquired:
                    try:
                        self.lock.release()
                    except Exception:
                        pass
                time.sleep(0.1)
                continue
            
# Wrapper for different LLM APIs
class LLMWrapper:
    """A unified wrapper for different LLM APIs"""
    def __init__(self, llm_name: str, tokens_per_minute: int = 80000):
        self.model_name = llm_name.upper()
        self.api_key = config.get_api_key(llm_name)
        self.temperature = float(config.TEMPERATURE)
        self.max_tokens = 4096
        self.rate_limiter = TokenRateLimiter(tokens_per_minute)
        self.logger = logger
        self.retrier = APICallRetrier()
        self._setup_client()
        
    def __enter__(self):
        """Context manager entry"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - ensure proper cleanup"""
        self.cleanup()
    
    def cleanup(self):
        """Clean up resources"""
        try:
            self.rate_limiter.shutdown()
            self.rate_limiter.cleanup()
        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}")

    def _setup_client(self):
        """Sets up the appropriate client and model configuration"""
        if self.model_name == "CLAUDE":
            self.client = Anthropic(api_key=self.api_key)
            self.model = "claude-3-5-sonnet-20241022"
            self.get_raw_response = self.claude_get_response
        elif self.model_name == "OPENAI":
            self.client = OpenAI(api_key=self.api_key)
            self.model = "gpt-4o-mini"
            self.get_raw_response = self.openai_get_response
        elif self.model_name == "LLAMA":
            self.client = LlamaAPI(self.api_key)
            self.get_raw_response = self.llama_get_response
            self.model = "llama3.2-90b-vision"
        elif self.model_name == "GEMINI":
            genai.configure(api_key=self.api_key)
            self.model = "gemini-2.0-flash-exp"
            self.client = genai.GenerativeModel(self.model)
            self.get_raw_response = self.gemini_get_response
        else:
            raise ValueError(f"Invalid LLM name: {self.model_name}")

    def get_response(self, prompt: str):
        """Returns the response from the LLM"""
        # Estimate the number of tokens, 3 characters per token
        estimated_tokens = len(prompt) / 3
        try:
            # Wait if necessary to stay within rate limits
            self.rate_limiter.wait_if_needed(estimated_tokens)
            
            def api_call():
                response, usage = self.get_raw_response(prompt)
                # Record usage
                self.rate_limiter.record_usage(usage)
                return response
            
            response = self.retrier.execute(api_call)
            return response
        except Exception as e:
            self.logger.error(f"Error in LLMWrapper.get_response: {e}")
            raise e
    
    ### May want to increase the specificity of these system prompt depending on the outcome ###
    ### or add a system prompt to the LLM since it seems they all allow for it###
    
    # OpenAI Wrapper
    def openai_get_response(self, prompt: str) -> Tuple[str, Optional[TokenUsage]]:
        """Returns the response from the LLM"""
        # Run the request
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "user", "content": prompt}
                      ],
            temperature=self.temperature,
        )
        # Usage statistics
        usage = TokenUsage(
            input_tokens=response.usage.prompt_tokens,
            output_tokens=response.usage.completion_tokens
        )
        return response.choices[0].message.content, usage
    
    # Claude Wrapper
    def claude_get_response(self, prompt: str) -> Tuple[str, Optional[TokenUsage]]:
        """Returns the response from the LLM"""
        # Run the request
        response = self.client.messages.create(
            model=self.model,
            max_tokens=self.max_tokens,
            temperature=self.temperature,
            messages=[
                {"role": "user", "content": prompt}
                      ],
        )
        # Usage statistics
        usage = TokenUsage(
            input_tokens=response.usage.input_tokens,
            output_tokens=response.usage.input_tokens
        )
        return response.content[0].text, usage
    
    # Llama Wrapper
    def llama_get_response(self, prompt: str):
        """Returns the response from the LLM"""
        # Run the request
        response = self.client.run({
            "model": self.model,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
        })
        # Usage statistics
        usage = TokenUsage(
            input_tokens=response['usage']['prompt_tokens'],
            output_tokens=response['usage']['completion_tokens']
        )
        # Parse the response
        return response.json()['choices'][0]['message']['content'], usage
    
    # Gemini Wrapper
    def gemini_get_response(self, prompt: str):
        """Returns the response from the LLM"""
        generation_config = genai.types.GenerationConfig(
            temperature=self.temperature,
            # This along with temperature controls diversity
            top_p=0.95, # Consider tokens makeing up top_p of the distribution
            top_k=30, # Consider top k tokens
            max_output_tokens=self.max_tokens,
        )
        # Generate the response
        response = self.client.generate_content(prompt, generation_config=generation_config)
        # Usage statistics
        usage = TokenUsage(
            input_tokens=response.usage_metadata.prompt_tokens,
            output_tokens=response.usage_metadata.candidates_token_count
        )
        return response.text.strip(), usage
