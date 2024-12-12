from dataclasses import dataclass
from typing import List
import os
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
from datetime import datetime, timedelta
from collections import deque
import threading

from llm_wrapper import LLMWrapper
from structures import ResearchTopic, SearchResults, ResearchPaper, ResearchAnalysis, ResearchAnalysisResult, TokenUsage
from prompts import formulate_topic_importance, formulate_topic_summary, formulate_new_research

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

class ConcurrentResearchAnalyzer:
    """A class to analyze research"""
    
    def __init__(self, llm_name: str, max_workers: int = 8, tokens_per_minute: int = 80000):
        self.llm = LLMWrapper(llm_name, tokens_per_minute)
        self.logger = logger
        self.max_workers = max_workers
        
    def analyze_research(self, search_result: SearchResults) -> ResearchAnalysisResult:
        """Analyzes the different research topics and Papers"""
        
        try:
            self.logger.info(f"Analyzing research: {search_result.research}...")
            research_analyses = []
            
            with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                futures = [executor.submit(self._analyze_topic, search_result.research, topic) for topic in search_result.research_topics]
                for future in as_completed(futures):
                    research_analyses.append(future.result())
                
            self.logger.info(f"Research analysis finished: {search_result.research}....")
            return ResearchAnalysisResult(
                main_topic=search_result.research,
                research_analyses=research_analyses,
            )
        except Exception as e:
            self.logger.error(f"Error analyzing research: {e}")
            raise e
    
    def _analyze_topic(self, main_research: str, topic: ResearchTopic) -> ResearchAnalysis:
        """Analyzes a research topic"""
        try:
            self.logger.info(f"Analyzing topic: {topic.topic}...")
            research_analysis = self._analyze_papers(main_research, topic)
            research_analysis.topic_summary = self._generate_topic_summary(research_analysis)
            research_analysis.new_research = self._generate_new_research(research_analysis, main_research)
            return research_analysis
        except Exception as e:
            self.logger.error(f"Error analyzing topic: {e}")
            raise e

    def _analyze_papers(self, main_research: str, topic: ResearchTopic) -> ResearchAnalysis:
        """Analyzes the papers for a given research topic"""
        try:
            self.logger.info(f"Analyzing papers for topic: {topic.topic}...")
            paper_analyses = []
            for paper in topic.research_papers:
                self.logger.info(f"Analyzing paper: {paper.title}...")
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
        
    def _generate_topic_summary(self, research_analysis: ResearchAnalysis) -> str:
        """Generates a summary for a research topic"""
        try:
            self.logger.info(f"Generating topic summary for topic: {research_analysis.topic.topic}...")
            paper_summaries = "\n\n".join([
                f"Paper Analysis {i+1}:\n{analysis}" 
                for i, analysis in enumerate(research_analysis.paper_analyses)
            ])
            prompt = formulate_topic_summary(research_analysis.topic.topic, paper_summaries)
            topic_summary = self.llm.get_response(prompt)
        except Exception as e:
            self.logger.error(f"Error generating topic summary: {e}")
            raise e
        return topic_summary
    
    def _generate_new_research(self, research_analysis: ResearchAnalysis, original_reseach:str) -> str:
        """Generates a new research prompt"""
        try:
            prompt = formulate_new_research(original_reseach, research_analysis.topic.topic, research_analysis.topic_summary)
            new_research = self.llm.get_response(prompt)
        except Exception as e:
            self.logger.error(f"Error generating new research: {e}")
            raise e
        return new_research
     
    def _generate_final_summary(self, research_analyses: List[ResearchAnalysis]):
        pass
    
    
        