import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
import os

from utils import ResearchPaper
from llm_wrapper import LLMWrapper
from manager import ResearchManager

log_path = "logs"
if not os.path.exists(log_path):
    os.makedirs(log_path)
    
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
log_file = os.path.join(log_path, "research_assistant.log")
handler = logging.FileHandler(log_file)
formatter = logging.Formatter("%(asctime)s -  %(levelname)s - %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)

class ResearchAssistant:
    """A class to assist with research through LLMs and Arxiv"""
    
    def __init__(self, llm_name: str, max_papers: int = 5):
        self.manager = ResearchManager(llm_name)
        self.max_papers = max_papers
        self.logger = logging.getLogger(__name__)
    
    # Generates a query for arXiv (Possibly make this more sophisticated)
    # Make a reshuffle if articles are found in search
    def generate_query(self, topic: str):
        """Generates a query for arXiv"""
        # Check if the topic is less than 8 words
        if len(topic.split(" ")) <= 8:
            return topic
        # Otherwise, generate a query
        prompt = formulate_search_query(topic)
        return self.llm.get_response(prompt)
    
    # Searches for papers, checks for relevance, and downloads them
    def find_papers(self, query: str, max_results: int = 10, max_workers: int = 10):
        """Searches for papers on arXiv"""
        # Search for papers
        results = search.search_arxiv(query, max_results)
        
        # Check the relevance of the articles
        valid_articles = []
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_result = {executor.submit(assess_relevence, result): result for result in results}
            for future in as_completed(future_to_result):
                result = future_to_result[future]
                try:
                    if future.result():
                        valid_articles.append(result)
                except Exception as exc:
                    print(f"{result.entry_id} generated an exception: {exc}")

        research_papers = download_papers(valid_articles)
        
        return valid_results

    # Assesses the relevance of a paper based on the abstract
    def assess_relevence(self, result):
        """Assesses the relevance of a paper"""
        # Check the relevance of the articles
        prompt = assess_relevence_prompt(result.summary)
        return self.llm.get_response()

        
