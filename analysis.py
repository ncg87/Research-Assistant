from dataclasses import dataclass
from typing import List
import os
import logging

from llm_wrapper import LLMWrapper
from structures import ResearchTopic, SearchResults, ResearchPaper, ResearchAnalysis
from prompts import formulate_topic_importance, formulate_topic_summary
    
@dataclass
class ResearchAnalysisResult:
    """Contains the analysis of a research topic"""
    main_topic: str
    research_analysis: List[ResearchAnalysis]
    final_summary: str

# Sets up logging
log_directory = 'logs'
if not os.path.exists(log_directory):
    os.makedirs(log_directory)
    
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
log_file = os.path.join(log_directory, "llm_analyzer.log")
handler = logging.FileHandler(log_file)
formatter = logging.Formatter("%(asctime)s -  %(levelname)s - %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)

class ResearchAnalyzer:
    """A class to analyze research"""
    
    def __init__(self, llm_name: str):
        self.llm = LLMWrapper(llm_name)
        self.logger = logger
        
    def analyze_research(self, search_result: SearchResult):
        """Analyzes the different research topics and Papers"""
        
        try:
            self.logger.info(f"Analyzing research: {search_result.research}...")
            research_analyses = []
            for topic in search_result.research_topics:
                # Analyze the papers for the topic
                research_analysis = self._analyze_papers(search_result.research, topic)
                # Generate a summary for the topic
                research_analyses.append(self._generate_topic_summary(research_analysis))
                
            final_summary = self._generate_final_summary(research_analyses)
        except Exception as e:
            self.logger.error(f"Error analyzing research: {e}")
            raise e
        
    def _analyze_papers(self, main_research: str, topic: ResearchTopic) -> ResearchAnalysis:
        """Analyzes the papers for a given research topic"""
        try:
            
            paper_analyses = []
            for paper in topic.research_papers:
                
                prompt = formulate_topic_importance(main_research, topic.topic, paper)     
                analysis = self.llm.get_response(prompt)
                paper_analyses.append(analysis)
                
        except Exception as e:
            self.logger.error(f"Error analyzing papers: {e}")
            raise e
            
        return ResearchAnalysis(
            topic=topic,
            paper_analyses=paper_analyses,
        )
        
    def _generate_topic_summary(self, research_analysis: ResearchAnalysis) -> ResearchAnalysis:
        """Generates a summary for a research topic"""
        
        prompt = formulate_topic_summary(research_analysis)
        research_analysis.topic_summary = self.llm.get_response(prompt)
        return research_analysis
     
    def _generate_final_summary(self, research_analyses: List[ResearchAnalysis]):
        pass
        

    
        