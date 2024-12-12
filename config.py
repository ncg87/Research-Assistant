import os
import dotenv

class Config:
    """A class to store configuration"""
    def __init__(self):
        # Load the environment variables
        dotenv.load_dotenv()
        # Store the API keys
        self.CLAUDE_API_KEY = os.getenv("CLAUDE_API_KEY")
        self.OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
        self.LLAMA_API_KEY = os.getenv("LLAMA_API_KEY")
        self.GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
        
        self.API_KEYS = {
            "CLAUDE": self.CLAUDE_API_KEY,
            "OPENAI": self.OPENAI_API_KEY,
            "LLAMA": self.LLAMA_API_KEY,
            "GEMINI": self.GEMINI_API_KEY
        }
        # Temperature
        self.TEMPERATURE = os.getenv("TEMPERATURE")
    
    def get_default_model(self) -> Optional[str]:
        """Returns the first available model as default"""
        available = self.get_available_models()
        return available[0] if available else None
    
    def has_any_api_keys(self) -> bool:
        """Check if any API keys are configured"""
        return any(key is not None for key in self.api_keys.values())
    
    def get_available_llms(self):
        """Returns a list of available LLMs"""
        return [model for model, key in self.API_KEYS.items() if key is not None]
    
    # Returns the API key for a given LLM
    def get_api_key(self, llm_name: str):
        """Returns the API key for a given LLM"""
        
        # Convert to uppercase
        llm_name = llm_name.upper()
        
        # Return the API key
        if llm_name == "CLAUDE":
            return self.CLAUDE_API_KEY
        elif llm_name == "OPENAI":
            return self.OPENAI_API_KEY
        elif llm_name == "LLAMA":
            return self.LLAMA_API_KEY
        elif llm_name == "GEMINI":
            return self.GEMINI_API_KEY
        else:
            raise ValueError(f"Invalid LLM name: {llm_name}")


