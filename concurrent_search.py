from dataclasses import dataclass
from datetime import datetime
from typing import List
import logging
import os 
import re
import json
import traceback
from concurrent.futures import ThreadPoolExecutor, as_completed

from prompts import formulate_research_topics, formulate_search_query, formulate_title_assesment, formulate_abstract_assesment
from llm_wrapper import LLMWrapper
from utils import search_relevent_arxiv, search_new_arxiv, download_papers
from structures import SearchResults, ResearchTopic, ResearchPaper

# Sets up logging
log_directory = 'logs'
if not os.path.exists(log_directory):
    os.makedirs(log_directory)
    
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
log_file = os.path.join(log_directory, "llm_search.log")
handler = logging.FileHandler(log_file)
formatter = logging.Formatter("%(asctime)s -  %(levelname)s - %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)
        
class ConcurrentResearchManager:
    """Manages the research process"""
    def __init__(self, llm_name: str):
        self.llm = LLMWrapper(llm_name)
        self.logger = logging.getLogger(__name__)
        self.max_workers = 8
        
    def research(self, research: str) -> SearchResults:
        """Analyzes the question and returns a list of research focus areas"""
        max_retries = 3
        try:
            self.logger.info(f"Analyzing research: {research}....")

            # Generates Topics
            research_topics = self._get_research_topics(research)
            # Conducts research for each topic
            research_topics = self._get_research_queries(research_topics)
            papers = self._get_papers(research_topics)
            
            research_results = []
            
            with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                futures = [executor.submit(self._research_topic, topic, papers) for topic in research_topics]
                for future in as_completed(futures):
                    research_results.append(future.result())
            
            # Return the research topics
            return SearchResults(
                research=research,
                research_topics=research_results
            )
            
        except Exception as e:
            self.logger.error(f"Error analyzing research: {e}")
            raise e
    
    def _get_research_topics(self, research: str, max_retries: int = 3)-> List[ResearchTopic]:
        """Extracts research topics from the research question"""
        try:    
            self.logger.info(f"Extracting research topics: {research}....")
            # Extracts 5 research topics to expand on original research
            for attempt in range(max_retries):
                # Generates research topic based on the original research question
                prompt = formulate_research_topics(research)
                response = self.llm.get_response(prompt)
                # Parses the response into a list of research focus areas
                research_topics = self._parse_research_topics(response)
                # If the research topics are found, return them
                if research_topics:
                    return research_topics
            # If all attempts fail, raise an exception
            raise Exception("Failed to extract research topics")
        # Error handling     
        except Exception as e:
            self.logger.error(f"Error extracting research topics: {e}")
            raise e
    
    def _parse_research_topics(self, response: str)-> List[ResearchTopic]:
        """
        Parses the response into a list of research focus areas
        Args:
            text (str): Input text containing numbered topics and priorities
                    
        Returns:
            list: List of dictionaries containing topic and priority
        """
        # Splits the response into lines and remove empty lines
        lines = [line.strip() for line in response.split('\n') if line.strip()]
        
        research_topics = []
        current_topic = ""
        
        for line in lines:
            # Check if line starts with a number followed by a period
            if re.match(r'^\d+\.', line):
                current_topic = line.split('.', 1)[1].strip()
            # Check if line contains priority
            elif line.startswith('Priority:'):
                priority = int(line.split(':')[1].strip())
                research_topics.append(ResearchTopic(
                    topic=current_topic,
                    priority=priority
                    ))
        # Return the list of research topics
        return research_topics
    
    def _conduct_research(self, research_topic: ResearchTopic, max_retries: int = 3)-> ResearchTopic:
        """Conducts research for a single topic"""
        try:
            self.logger.info(f"Conducting research for topic: {research_topic.topic}....")
            for attempt in range(max_retries):
                # Generate a search query for the topic
                prompt = formulate_search_query(research_topic.topic, previous_topics)
                response = self.llm.get_response(prompt)
                previous_topics += response + ", "
                research_topic.query = response
        except Exception as e:
            self.logger.error(f"Error conducting research: {e}")
            raise e
    def _get_research_queries(self, research_topics: List[ResearchTopic]):
        try:
            self.logger.info(f"Generating search queries for {len(research_topics)} research topics....")
            
            previous_topics = ""
            
            # Generate a search query for each research topic
            for topic in research_topics:
                prompt = formulate_search_query(topic.topic, previous_topics)
                response = self.llm.get_response(prompt)
                previous_topics += response + ", "
                topic.query = response
            return research_topics
        except Exception as e:
            self.logger.error(f"Error generating search queries: {e}")
            raise e
        
    def _get_papers(self, research_topics: List[ResearchTopic]):
        """Gets possible papers from arXiv"""
        try:
            self.logger.info(f"Getting papers for {len(research_topics)} research topics....")
            papers = []
            # Get a list of possible papers to probe
            for topic in research_topics:
                # Get relevent papers for each query
                papers.extend(search_relevent_arxiv(topic.query))
                papers.extend(search_new_arxiv(topic.query))
                
            return papers

        except Exception as e:
            self.logger.error(f"Error getting papers: {e}")
            raise e
            
    def _research_topic(self, research_topic: ResearchTopic, papers: List[ResearchPaper]):
        """Conducts research for a single topic"""
        try:
            self.logger.info(f"Conducting research for topic: {research_topic.topic}....")
            # Check the relevence of the titles of the papers
            title_indices = self._check_title(research_topic, papers)
            # Check the relevence of the abstracts of the papers
            research_topic = self._check_abstract(research_topic, papers, title_indices)
            return research_topic
        except Exception as e:
            self.logger.error(f"Error conducting research: {e}")
            raise e
    
    def _check_title(self, research_topic: ResearchTopic, papers: List[ResearchPaper], max_titles = 6):
        """Checks the relevence of a titles of a list of research papers to a research topic"""
        try:
            self.logger.info(f"Checking relevence of {len(papers)} papers for {research_topic.topic}...")
            # Generate a string containing all papers
            paper_entries = "\n".join([
                f"[{i}] {paper.title}"
                for i, paper in enumerate(papers)
            ])
            prompt = formulate_title_assesment(paper_entries, research_topic.topic, max_titles)
            response = self.llm.get_response(prompt)
            # Convert to a list of numbers
            return json.loads(response)
            
        except Exception as e:
            self.logger.error(f"Error checking relevence: {e}")
            raise e
    def _check_abstract(self, research_topic: ResearchTopic, papers: List[ResearchPaper], title_indices: List[int]):
        """Checks the relevence of the abstracts of a list of research papers to a research topic"""
        try:
            self.logger.info(f"Checking abstract relevence of {len(title_indices)} papers for {research_topic.topic}...")
            # Get the relevent papers from title relevence
            relevent_papers = [papers[j] for j in title_indices]
            # Creates a string containing all the papers and titles
            paper_abstracts = "\n\n".join([
                f"[{i}]\nTitle:{paper.title}\n Abstract:{paper.summary}"
                for i, paper in enumerate(relevent_papers)
            ])
            # Check the relevance of the papers to the research topic
            prompt = formulate_abstract_assesment(paper_abstracts, research_topic.topic)
            response = self.llm.get_response(prompt)
            # Convert to a list of numbers
            paper_indices = json.loads(response)
            research_topic.research_papers = download_papers([relevent_papers[j] for j in paper_indices])
            return research_topic
        except Exception as e:
            self.logger.error(f"Error checking abstract relevence: {e}")
            raise e
