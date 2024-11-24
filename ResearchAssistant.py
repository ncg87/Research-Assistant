import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
import os

from utils import ResearchPaper
from llm_wrapper import LLMWrapper
from search import ResearchManager, SearchResults, ResearchTopic
from analysis import ResearchAnalyzer

log_path = "logs"
if not os.path.exists(log_path):
    os.makedirs(log_path)
    
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
log_file = os.path.join(log_path, "research_assistant.log")
handler = logging.FileHandler(log_path)
formatter = logging.Formatter("%(asctime)s -  %(levelname)s - %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)

class ResearchAssistant:
    """A class to assist with research through LLMs and Arxiv"""
    
    def __init__(self, llm_name: str, max_papers: int = 5):
        self.manager = ResearchManager(llm_name)
        self.analyzer = ResearchAnalyzer(llm_name)
        self.logger = logging.getLogger(__name__)
    
    def research(self, research: str):
        """Starts the research process"""
        
        try:
            self.logger.info(f"Starting research: {research}....")
            search_result = self.manager.analyze_research(research)
            self.analyzer.analyze_research(search_result)
        except Exception as e:
            self.logger.error(f"Error conducting research: {e}")
            raise e
        

        
