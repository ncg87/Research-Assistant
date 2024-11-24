import os
import logging
import json
from datetime import datetime
from typing import Optional, List, Dict, Any
from dataclasses import asdict

from structures import ResearchPaper, ResearchAnalysis, ResearchAnalysisResult


# Sets up logging
log_directory = 'logs'
if not os.path.exists(log_directory):
    os.makedirs(log_directory)
    
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
log_file = os.path.join(log_directory, "research_saver.log")
handler = logging.FileHandler(log_file)
formatter = logging.Formatter("%(asctime)s -  %(levelname)s - %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)

class ResearchSaver:
    """A class to save research analyses"""
    
    def __init__(self, base_directory: str = "research_results"):
        self.base_directory = base_directory
        self._ensure_directory_exists(self.base_directory)
        self.logger = logging.getLogger(__name__)
        
    def _ensure_directory_exists(self, directory: str):
        """Ensures a directory exists"""
        if not os.path.exists(directory):
            os.makedirs(directory)
    
    def _create_research_directory(self, main_topic: str) -> str:
        """Create a directory for a specific research topic"""
        # Clean the topic name for use as directory name
        clean_topic = "".join(c for c in main_topic if c.isalnum() or c in (' ', '-', '_')).rstrip()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        dir_name = f"{clean_topic}_{timestamp}"
        full_path = os.path.join(self.base_directory, dir_name)
        os.makedirs(full_path)
        return full_path
    
    def _serialize_paper(self, paper: ResearchPaper) -> Dict[str, Any]:
        """Converts a research paper into a serializable dictionary"""
        self.logger.info(f"Serializing paper: {paper.title}...")
        paper_dict = asdict(paper)
        paper_dict["authors"] = [str(author) for author in paper.authors]
        # Adjust the pdf path to the relative directory
        if paper.pdf_path:
            paper_dict["pdf_path"] = os.path.basename(paper.pdf_path)
        
        return paper_dict
    
    def _save_topic_analysis(self, research_analysis: ResearchAnalysis, research_directory: str):
        """Saves the information for a single topic"""
        self.logger.info(f"Saving topic analysis for {research_analysis.topic.topic}...")
        topic_dict = {
            'topic': research_analysis.topic.topic,
            'priority': research_analysis.topic.priority,
            'query': research_analysis.topic.query,
            'timestamp': research_analysis.topic.timestamp,
            'papers': [self._serialize_paper(paper) for paper in research_analysis.topic.research_papers],
            'paper_analyses': research_analysis.paper_analyses,
            'topic_summary': research_analysis.topic_summary
        }
        # Create a clean filename for the topic
        clean_topic = "".join(c for c in research_analysis.topic.topic if c.isalnum() or c in (' ', '-', '_')).rstrip()
        filename = f"{clean_topic}.json"
        filepath = os.path.join(research_directory, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(topic_dict, f, indent=2, ensure_ascii=False)
    
    def save_results(self, research_result: ResearchAnalysisResult):
        """Save the complete research analysis result"""

        try:
            logger.info(f"Saving research results for {research_result.main_topic}...")
            # Create main directory
            research_directory = self._create_research_directory(research_result.main_topic)
            # Save each individual topic analysis
            for analysis in research_result.research_analyses:
                self._save_topic_analysis(analysis, research_directory)
            # Save the final summary
            if research_result.final_summary:
                summary_path = os.path.join(research_directory, "final_summary.txt")
                with open(summary_path, 'w', encoding='utf-8') as f:
                    f.write(research_result.final_summary)
            # Save metadata
            metadata = {
                'main_topic': research_result.main_topic,
                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'num_topics': len(research_result.research_analyses),
                'topics': [ra.topic.topic for ra in research_result.research_analyses]
            }
            
            metadata_path = os.path.join(research_directory, "metadata.json")
            with open(metadata_path, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)
                
            return research_directory     
            
        except Exception as e:
            self.logger.error(f"Error saving research results: {e}")
            raise e
            
