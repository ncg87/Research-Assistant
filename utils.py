import arxiv
import pymupdf
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
import logging
from dataclasses import dataclass
from typing import List, Optional, Tuple  
import re


from structures import ResearchPaper, ResearchAnalysis


log_directory = 'logs'
if not os.path.exists(log_directory):
    os.makedirs(log_directory)
    
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
log_file = os.path.join(log_directory, "utils.log")
handler = logging.FileHandler(log_file)
formatter = logging.Formatter("%(asctime)s -  %(levelname)s - %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)


# Searchs for papers and returns them in a list
def search_relevent_arxiv(query: str, max_results: int = 5):
    """Searches for papers on arXiv"""
    try:
        # Configure the client
        client = arxiv.Client(
            page_size = max_results,
            delay_seconds = 3.0,
            num_retries = 3,
        )
        # Configure the search
        search = arxiv.Search(
            query = query,
            max_results = max_results,
            sort_by = arxiv.SortCriterion.Relevance,
        )
        # Returns a list of results (since we can call .download_pdf on them)
        return list(client.results(search))
    except Exception as e:
        print(f"Error searching for papers: {e}")
        return []

# Searchs for papers and returns them in a list
def search_new_arxiv(query: str, max_results: int = 5):
    """Searches for papers on arXiv"""
    try:
        # Configure the client
        client = arxiv.Client(
            page_size = max_results,
            delay_seconds = 3.0,
            num_retries = 3,
        )
        # Configure the search
        search = arxiv.Search(
            query = query,
            max_results = max_results,
            sort_by = arxiv.SortCriterion.SubmittedDate, 
        )
        # Returns a list of results (since we can call .download_pdf on them)
        return list(client.results(search))
    except Exception as e:
        print(f"Error searching for papers: {e}")
        return []


def get_pdf(result, path):
    return result.download_pdf(dirpath = path)

def download_papers(results, search_num = None, max_workers = 10):
    
    papers_dir = f"./papers/"
    # Creates a papers dir
    if not os.path.exists(papers_dir):
        os.makedirs(papers_dir)
    research_papers = []
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_result = {executor.submit(get_pdf, result, papers_dir): result for result in results}
        for future in as_completed(future_to_result):
            try:
                pdf_path = future.result()
                logger.info(f"Downloading {future_to_result[future].title} to {pdf_path} ....")
                paper = ResearchPaper(
                    title=future_to_result[future].title,
                    authors=future_to_result[future].authors,
                    abstract=future_to_result[future].summary,
                    url=future_to_result[future].entry_id,
                    pdf_path=pdf_path,
                    content=pdf_to_text(pdf_path)
                    )
                research_papers.append(paper)
            except Exception as exc:
                logger.info(f"{future_to_result[future].entry_id} generated an exception: {exc}")
    
    return research_papers

def pdf_to_text(pdf_path):
    """Converts a PDF to text"""
    # Open the PDF file
    pdf = pymupdf.open(pdf_path)
    text = ""
    # Iterate through each page and add the text to the string
    for page in pdf:
        text += page.get_text()
    # Return the text
    return text

def split_into_sections(text: str) -> List[str]:
    """Split text into sections based on common research paper headers"""
    section_headers = [
        "abstract", "introduction", "background", "related work",
        "methodology", "method", "approach", "implementation",
        "results", "evaluation", "discussion", "conclusion",
        "future work", "references"
    ]
    
    # Add common section number patterns
    numbered_patterns = [
        r'\d+\.\s+\w+',  # "1. Introduction"
        r'[IVX]+\.\s+\w+',  # "IV. Results"
    ]
    
    current_section = ""
    sections = []
    lines = text.split('\n')
    
    for line in lines:
        line_lower = line.lower().strip()
        
        # Check if line is a section header
        is_header = (
            line_lower in section_headers or
            any(re.match(pattern, line, re.IGNORECASE) for pattern in numbered_patterns)
        )
        
        if is_header:
            if current_section:
                sections.append(current_section)
            current_section = line + "\n"
        else:
            current_section += line + "\n"
            
    if current_section:
        sections.append(current_section)
        
    return sections

def create_chunks_with_sections(text: str, chunk_size: int = 4000) -> List[Tuple[str, str]]:
    """Creates chunks while preserving section context"""
    sections = split_into_sections(text)
    chunks = []
    current_chunk = ""
    current_section = ""
    
    for section in sections:
        # If adding this section would exceed chunk size
        if len(current_chunk) + len(section) > chunk_size:
            if current_chunk:
                chunks.append((current_section, current_chunk))
            current_chunk = section
            current_section = section.split('\n')[0]  # First line is header
        else:
            current_chunk += section
            if not current_section:
                current_section = section.split('\n')[0]
    
    if current_chunk:
        chunks.append((current_section, current_chunk))
        
    return chunks

