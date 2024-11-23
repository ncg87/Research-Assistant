# LLM choices
from openai import OpenAI
from anthropic import Anthropic
from llamaapi import LlamaAPI
import google.generativeai as genai

# Configuration
from config import Config

config = Config()

# Wrapper for different LLM APIs
class LLMWrapper:
    """A unified wrapper for different LLM APIs"""
    def __init__(self, llm_name: str):
        self.model_name = llm_name.upper()
        self.api_key = config.get_api_key(llm_name)
        self.temperature = float(config.TEMPERATURE)
        self.max_tokens = 4096
        self.request_times = []
        
        self._setup_client()

    def _setup_client(self):
        """Sets up the appropriate client and model configuration"""
        if self.model_name == "CLAUDE":
            self.client = Anthropic(api_key=self.api_key)
            self.model = "claude-3-5-sonnet-20241022"
            self.get_response = self.claude_get_response
        elif self.model_name == "OPENAI":
            self.client = OpenAI(api_key=self.api_key)
            self.model = "gpt-4o-mini"
            self.get_response = self.openai_get_response
        elif self.model_name == "LLAMA":
            self.client = LlamaAPI(self.api_key)
            self.get_response = self.llama_get_response
            self.model = "llama3.2-90b-vision"
        elif self.model_name == "GEMINI":
            genai.configure(api_key=self.api_key)
            self.model = "gemini-1.5-flash"
            self.client = genai.GenerativeModel(self.model)
            self.get_response = self.gemini_get_response
        else:
            raise ValueError(f"Invalid LLM name: {self.model_name}")

    ### May want to increase the specificity of these system prompt depending on the outcome ###
    ### or add a system prompt to the LLM since it seems they all allow for it###
    
    # OpenAI Wrapper
    def openai_get_response(self, prompt: str):
        """Returns the response from the LLM"""
        # Run the request
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "user", "content": prompt}
                      ],
            temperature=self.temperature,
        )
        return response.choices[0].message.content
    
    # Claude Wrapper
    def claude_get_response(self, prompt: str):
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
        return response.content[0].text
    
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
        # Parse the response
        return response.json()['choices'][0]['message']['content']
    
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
        return response.text.strip()


