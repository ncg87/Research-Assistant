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
        # Temperature
        self.TEMPERATURE = os.getenv("TEMPERATURE")
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


