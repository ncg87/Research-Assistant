import logging
import os
from typing import List
from utils import ResearchPaper
from llm_wrapper import LLMWrapper
from structures import ResearchAnalysis, SearchResults, ResearchTopic
from search import ResearchManager 
from analysis import ResearchAnalyzer

# Sets up logging
log_directory = 'logs'
if not os.path.exists(log_directory):
    os.makedirs(log_directory)
    
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
log_file = os.path.join(log_directory, "research_assistant.log")
handler = logging.FileHandler(log_file)
formatter = logging.Formatter("%(asctime)s -  %(levelname)s - %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)

class ResearchAssistant:
    """A class to assist with research through LLMs and Arxiv"""
    
    def __init__(self, llm_name: str):
        self.manager = ResearchManager(llm_name)
        self.analyzer = ResearchAnalyzer(llm_name)
        self.logger = logging.getLogger(__name__)
    
    def research(self, research: str) -> List[ResearchAnalysis]:
        """Starts the research process"""
        
        try:
            self.logger.info(f"Starting research: {research}....")
            search_result = self.manager.research(research)
            research_analyses = self.analyzer.analyze_research(search_result)
            return research_analyses
        except Exception as e:
            self.logger.error(f"Error conducting research: {e}")
            raise e
    
    def _save_research_analyses(self, research_analyses: List[ResearchAnalysis]):
        """Saves the research analyses to a file"""
        pass

        
