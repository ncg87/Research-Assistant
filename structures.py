from datetime import datetime
from typing import List, Optional
from dataclasses import dataclass

@dataclass
class ResearchPaper:
    """A class to store a research paper"""
    title: str
    authors: List
    abstract: str
    url: str
    pdf_path: Optional[str] = None
    content: Optional[str] = None


@dataclass
class ResearchTopic:
    """Represents a specific area of research topic"""
    topic: str
    priority: int
    query: str = ""
    timestamp: str = ""
    research_papers: List[ResearchPaper] = None

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
@dataclass
class SearchResults:
    """Contains the complete analysis result"""
    research: str
    research_topics: List[ResearchTopic]
    timestamp: str = ""

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

@dataclass
class ResearchAnalysis:
    """Contains the analysis of a research topic"""
    topic: ResearchTopic
    paper_analyses: List[str]
    topic_summary: str = None
    new_research: str = None

@dataclass
class ResearchAnalysisResult:
    """Contains the analysis of a research topic"""
    main_topic: str
    research_analyses: List[ResearchAnalysis]
    final_summary: str = None
    