import arxiv
import pymupdf
import os
from concurrent.futures import ThreadPoolExecutor, as_completed

from dataclasses import dataclass
from typing import List, Optional    

@dataclass
class ResearchPaper:
    """A class to store a research paper"""
    title: str
    authors: List[str]
    abstract: str
    url: str
    pdf_path: Optional[str] = None
    content: Optional[str] = None


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

def pdf_to_text(pdf):
    return pdf.read_text()

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
                print(f"Downloading {future_to_result[future].title} to {pdf_path} ....")
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
                print(f"{future_to_result[future].entry_id} generated an exception: {exc}")
    
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

def parse_citations(text):
    """Parses citations from a string of text"""
    pass
