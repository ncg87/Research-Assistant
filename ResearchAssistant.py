import logging
import os
from typing import List
from utils import ResearchPaper
from llm_wrapper import LLMWrapper
from structures import ResearchAnalysis, SearchResults, ResearchTopic, ResearchAnalysisResult
from search import ResearchManager 
from analysis import ResearchAnalyzer
from saver import ResearchSaver

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
    
    def __init__(self, llm_name: str, save_dir : str ="./research_results"):
        self.save_dir = save_dir
        self.researcher = ResearchManager(llm_name)
        self.analyzer = ResearchAnalyzer(llm_name)
        self.saver = ResearchSaver(save_dir)
        self.logger = logging.getLogger(__name__)
    
    def new_research(self, research: str) -> ResearchAnalysisResult:
        """Starts the research process"""
        
        try:
            self.logger.info(f"Starting research: {research}....")
            search_result = self.researcher.research(research)
            research_analyses = self.analyzer.analyze_research(search_result)
            self._save_research_analyses(research_analyses)
        except Exception as e:
            self.logger.error(f"Error conducting research: {e}")
            raise e
    
    def _save_research_analyses(self, research_results: ResearchAnalysisResult, save_directory: str = "./research_results"):
        """Saves the research analyses to a file"""
    
        try:
            self.logger.info(f"Saving research results of {research_results.main_topic} to {save_directory}...")
            self.saver.save_results(research_results, save_directory)
            
        except Exception as e:
            self.logger.error(f"Error saving research analyses: {e}")
            raise e
        
        
