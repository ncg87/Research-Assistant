from dataclasses import dataclass
from typing import List, Dict
import os
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
import threading

from llm_wrapper import LLMWrapper
from structures import ResearchTopic, SearchResults, ResearchPaper, ResearchAnalysis, ResearchAnalysisResult
from prompts import (
    formulate_paper_extraction,
    formulate_paper_analysis,
    formulate_theme_identification,
    formulate_topic_summary,
    formulate_new_research_direction
)

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
    """Analyzes research with concurrent topic processing"""
    
    def __init__(self, llm_name: str):
        self.llm = LLMWrapper(llm_name)
        self.logger = logger
        self.max_workers = 4
        self.delay_between_calls = 2
        self.api_lock = threading.Lock()
        
    def _rate_limited_llm_call(self, prompt: str) -> str:
        """Makes an LLM API call with rate limiting"""
        with self.api_lock:
            time.sleep(self.delay_between_calls)
            return self.llm.get_response(prompt)

    def analyze_research(self, search_result: SearchResults) -> ResearchAnalysisResult:
        """Main analysis method with concurrent topic processing"""
        try:
            self.logger.info(f"Analyzing research: {search_result.research}...")
            research_analyses = []
            
            # Process topics concurrently
            with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                # Submit each topic for analysis
                future_to_topic = {
                    executor.submit(
                        self._analyze_topic,
                        search_result.research,
                        topic
                    ): topic for topic in search_result.research_topics
                }
                
                # Collect results as they complete
                for future in as_completed(future_to_topic):
                    topic = future_to_topic[future]
                    try:
                        analysis = future.result()
                        research_analyses.append(analysis)
                        self.logger.info(f"Completed analysis of topic: {topic.topic}")
                    except Exception as e:
                        self.logger.error(f"Topic analysis failed for {topic.topic}: {e}")
            
            return ResearchAnalysisResult(
                main_topic=search_result.research,
                research_analyses=research_analyses
            )
        except Exception as e:
            self.logger.error(f"Error analyzing research: {e}")
            raise e
    
    def _analyze_topic(self, main_research: str, topic: ResearchTopic) -> ResearchAnalysis:
        """Analyzes a topic and its papers sequentially"""
        try:
            self.logger.info(f"Analyzing topic: {topic.topic}...")
            paper_analyses = []
            
            # Process papers sequentially for each topic
            for paper in topic.research_papers:
                try:
                    analysis = self._analyze_paper(main_research, topic.topic, paper)
                    paper_analyses.append(analysis)
                    self.logger.info(f"Completed analysis of paper: {paper.title}")
                except Exception as e:
                    self.logger.error(f"Paper analysis failed for {paper.title}: {e}")
                    raise e
            
            analysis = ResearchAnalysis(
                topic=topic,
                paper_analyses=paper_analyses
            )
            
            # Generate topic summary and new research
            analysis.topic_summary = self._generate_topic_summary(analysis)
            analysis.new_research = self._generate_new_research(analysis, main_research)
            
            return analysis
            
        except Exception as e:
            self.logger.error(f"Error analyzing topic: {e}")
            raise e

    def _analyze_paper(self, main_research: str, topic: str, paper: ResearchPaper) -> str:
        """Analyzes a single paper sequentially"""
        try:
            # Phase 1: Extract key information
            extraction_prompt = formulate_paper_extraction(
                paper_title=paper.title,
                paper_authors=paper.authors,
                paper_content=paper.content
            )
            extracted_info = self._rate_limited_llm_call(extraction_prompt)

            # Phase 2: Analyze extracted information
            analysis_prompt = formulate_paper_analysis(
                main_research=main_research,
                topic=topic,
                paper_title=paper.title,
                paper_abstract=paper.abstract,
                extracted_info=extracted_info
            )
            return self._rate_limited_llm_call(analysis_prompt)

        except Exception as e:
            self.logger.error(f"Error in paper analysis: {e}")
            raise e

    def _generate_topic_summary(self, research_analysis: ResearchAnalysis) -> str:
        """Generates topic summary from sequential paper analyses"""
        try:
            # First identify themes
            theme_prompt = formulate_theme_identification(
                topic=research_analysis.topic.topic,
                paper_analyses=research_analysis.paper_analyses
            )
            themes = self._rate_limited_llm_call(theme_prompt)

            # Then generate comprehensive summary
            summary_prompt = formulate_topic_summary(
                topic=research_analysis.topic.topic,
                themes=themes,
                paper_analyses=research_analysis.paper_analyses
            )
            return self._rate_limited_llm_call(summary_prompt)

        except Exception as e:
            self.logger.error(f"Error generating topic summary: {e}")
            raise e

    def _generate_new_research(self, analysis: ResearchAnalysis, main_research: str) -> str:
        """Generates new research directions based on complete analysis"""
        try:
            prompt = formulate_new_research_direction(
                topic=analysis.topic.topic,
                topic_summary=analysis.topic_summary,
                main_research=main_research
            )
            return self._rate_limited_llm_call(prompt)

        except Exception as e:
            self.logger.error(f"Error generating new research directions: {e}")
            raise e