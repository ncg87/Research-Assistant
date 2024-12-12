from dataclasses import dataclass
from datetime import datetime
from typing import List
import logging
import os 
import re
import json
import traceback

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
        
class ResearchManager:
    """Manages the research process"""
    def __init__(self, llm_name: str):
        self.llm = LLMWrapper(llm_name)
        self.logger = logging.getLogger(__name__)
        
    def research(self, research: str):
        """Analyzes the question and returns a list of research focus areas"""
        max_retries = 3
        try:
            self.logger.info(f"Analyzing research: {research}....")

            # Generates Topics
            research_topics = self._get_research_topics(research, max_retries= max_retries)
            # Generates Queries for research topics
            research_topics = self._get_research_queries(research_topics)
            # Get list of possible papers from arXiv
            papers = self._get_papers(research_topics)
            title_indices = self._check_title_relevance(papers, research_topics)
            # Check the relevance of the papers to the research topics
            research_topics = self._check_abstract_relevence(papers, research_topics, title_indices)
            # Return the research topics
            return SearchResults(
                research=research,
                research_topics=research_topics
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
    
    def _check_title_relevance(self, papers, research_topics: List[ResearchTopic], max_titles = 6):
        """Check the relevence of a list of research papers by title"""
        try:
            self.logger.info(f"Checking title relevence of {len(papers)} for {len(research_topics)} topics...")
            # Generate a string containing all papers
            paper_entries = "\n".join([
                f"[{i}] {paper.title}"
                for i, paper in enumerate(papers)
            ])
            responses = []
            # Check the relevance of each paper to the research topic
            for topic in research_topics:
                prompt = formulate_title_assesment(paper_entries, topic.topic, max_titles   )
                response = self.llm.get_response(prompt)
                # Convert to a list of numbers
                responses.append(json.loads(response))
            # Return the indices of the relevent titles
            return responses
        except Exception as e:
            self.logger.error(f"Error checking relevance: {e}")
            raise e
    def _check_abstract_relevence(self, papers, research_topics: List[ResearchTopic], indices_list: List[List[int]]):
        """Check the relevence of a list of research papers by abstract"""
        try:
            self.logger.info(f"Checking abstract relevence of {len(indices_list) * len(indices_list[0])} papers for {len(research_topics)} topics...")
            # Iterates through each research topic
            for i, indices in enumerate(indices_list):
                topic = research_topics[i]
                # Get the relevent papers from title relevence
                condensed_papers = [papers[j] for j in indices]
                # Creates a string containing all the papers and titles
                paper_abstracts = "\n\n".join([
                    f"[{i}]\nTitle:{paper.title}\n Abstract:{paper.summary}"
                    for i, paper in enumerate(condensed_papers)
                ])
                # Check the relevance of the papers to the research topic
                prompt = formulate_abstract_assesment(paper_abstracts, topic.topic)
                response = self.llm.get_response(prompt)
                # Convert to a list of numbers
                paper_indices = json.loads(response)
                research_topics[i].research_papers = download_papers([condensed_papers[j] for j in paper_indices])
                
            return research_topics
        
        except Exception as e:
            self.logger.error(f"Error checking abstract relevence: {e}")
            raise e
