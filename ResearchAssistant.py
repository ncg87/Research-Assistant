import logging
import os
from typing import List
from utils import ResearchPaper
from llm_wrapper import LLMWrapper
from structures import ResearchAnalysis, SearchResults, ResearchTopic, ResearchAnalysisResult
from concurrent_search import ConcurrentResearchManager 
from concurrent_analysis import ConcurrentResearchAnalyzer
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
        self.researcher = ConcurrentResearchManager(llm_name)
        self.analyzer = ConcurrentResearchAnalyzer(llm_name)
        self.saver = ResearchSaver(save_dir)
        self.save_dir = save_dir
        self.logger = logger
    
    def _initialize_components(self):
        """Initialize or reinitialize all components with current LLM settings"""
        self.researcher = ConcurrentResearchManager(self.llm_name)
        self.analyzer = ConcurrentResearchAnalyzer(self.llm_name)
        self.saver = ResearchSaver(self.save_dir)
        
    def update_model(self, new_llm_name: str):
        """Update the LLM model and reinitialize all components"""
        self.llm_name = new_llm_name
        self._initialize_components()
        
    def new_research(self, research: str) -> ResearchAnalysisResult:
        """Starts the research process"""
        
        try:
            self.logger.info(f"Starting research: {research}....")
            search_result = self.researcher.research(research)
            
            self.logger.info(f"Research finished starting analysis: {research}....")
            research_analyses = self.analyzer.analyze_research(search_result)
            
            self.logger.info(f"Analysis finished saving results: {research}....")
            self._save_research_analyses(research_analyses)
            return research_analyses
        except Exception as e:
            self.logger.error(f"Error conducting research: {e}")
            raise e
    
    def _save_research_analyses(self, research_results: ResearchAnalysisResult):
        """Saves the research analyses to a file"""
    
        try:
            self.logger.info(f"Saving research results of {research_results.main_topic} to {self.save_dir}...")
            self.saver.save_results(research_results)
            
        except Exception as e:
            self.logger.error(f"Error saving research analyses: {e}")
            raise e
        
    
