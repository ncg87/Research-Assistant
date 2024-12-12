from dataclasses import dataclass
from typing import Dict, Optional, List
import threading
from enum import Enum
from queue import Queue
import time
from datetime import datetime

class ResearchStage(Enum):
    TOPIC_GENERATION = "topic_generation"
    QUERY_GENERATION = "query_generation"
    PAPER_SEARCH = "paper_search"
    TITLE_ANALYSIS = "title_analysis"
    ABSTRACT_ANALYSIS = "abstract_analysis"
    PAPER_DOWNLOAD = "paper_download"
    PAPER_ANALYSIS = "paper_analysis"
    TOPIC_SUMMARY = "topic_summary"
    NEW_RESEARCH = "new_research"

@dataclass
class ProgressEvent:
    stage: ResearchStage
    message: str
    progress: float  # 0.0 to 1.0
    topic_index: Optional[int] = None
    paper_index: Optional[int] = None
    total_topics: Optional[int] = None
    total_papers: Optional[int] = None
    timestamp: datetime = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()

class ProgressTracker:
    def __init__(self):
        self.events = Queue()
        self.stage_weights = {
            ResearchStage.TOPIC_GENERATION: 0.1,
            ResearchStage.QUERY_GENERATION: 0.1,
            ResearchStage.PAPER_SEARCH: 0.1,
            ResearchStage.TITLE_ANALYSIS: 0.1,
            ResearchStage.ABSTRACT_ANALYSIS: 0.1,
            ResearchStage.PAPER_DOWNLOAD: 0.1,
            ResearchStage.PAPER_ANALYSIS: 0.2,
            ResearchStage.TOPIC_SUMMARY: 0.1,
            ResearchStage.NEW_RESEARCH: 0.1
        }
        self.current_progress = {stage: 0.0 for stage in ResearchStage}
        self._lock = threading.Lock()

    def update_progress(self, event: ProgressEvent):
        """Update progress for a specific stage"""
        with self._lock:
            self.current_progress[event.stage] = event.progress
            self.events.put(event)

    def get_overall_progress(self) -> float:
        """Calculate overall progress based on weighted stages"""
        with self._lock:
            return sum(
                self.current_progress[stage] * weight
                for stage, weight in self.stage_weights.items()
            )

    def get_latest_event(self) -> Optional[ProgressEvent]:
        """Get the latest event if available"""
        try:
            return self.events.get_nowait()
        except:
            return None

class ResearchProgressMonitor:
    """Monitors and updates research progress in real-time"""
    
    def __init__(self, tracker: ProgressTracker):
        self.tracker = tracker
        self.total_topics = 0
        self.total_papers_per_topic = 0

    def start_research(self, num_topics: int, papers_per_topic: int):
        """Initialize a new research session"""
        self.total_topics = num_topics
        self.total_papers_per_topic = papers_per_topic

    def update_topic_generation(self, completed_topics: int):
        """Update progress for topic generation"""
        progress = completed_topics / self.total_topics
        self.tracker.update_progress(ProgressEvent(
            stage=ResearchStage.TOPIC_GENERATION,
            message=f"Generated {completed_topics}/{self.total_topics} research topics",
            progress=progress,
            total_topics=self.total_topics
        ))

    def update_paper_search(self, topic_index: int, found_papers: int):
        """Update progress for paper search"""
        topic_progress = (topic_index + 1) / self.total_topics
        self.tracker.update_progress(ProgressEvent(
            stage=ResearchStage.PAPER_SEARCH,
            message=f"Found {found_papers} papers for topic {topic_index + 1}",
            progress=topic_progress,
            topic_index=topic_index,
            total_topics=self.total_topics
        ))

    def update_paper_analysis(self, topic_index: int, paper_index: int):
        """Update progress for paper analysis"""
        topic_progress = topic_index / self.total_topics
        paper_progress = paper_index / self.total_papers_per_topic
        combined_progress = (topic_progress + paper_progress) / 2
        
        self.tracker.update_progress(ProgressEvent(
            stage=ResearchStage.PAPER_ANALYSIS,
            message=f"Analyzing paper {paper_index + 1}/{self.total_papers_per_topic} for topic {topic_index + 1}",
            progress=combined_progress,
            topic_index=topic_index,
            paper_index=paper_index,
            total_topics=self.total_topics,
            total_papers=self.total_papers_per_topic
        ))

    def update_topic_summary(self, topic_index: int):
        """Update progress for topic summary generation"""
        progress = (topic_index + 1) / self.total_topics
        self.tracker.update_progress(ProgressEvent(
            stage=ResearchStage.TOPIC_SUMMARY,
            message=f"Generating summary for topic {topic_index + 1}/{self.total_topics}",
            progress=progress,
            topic_index=topic_index,
            total_topics=self.total_topics
        ))