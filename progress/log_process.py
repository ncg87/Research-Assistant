
import logging
import os
from typing import Dict, Optional
from rich.progress import Progress, TaskID, TextColumn
from rich import box
from rich.console import Group
from rich.panel import Panel
import re
from progress.progress_tracking import ProgressTracker, ProgressEvent, ResearchStage
from datetime import datetime

class StatusProgress(Progress):
    """Custom Progress class that includes status messages"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.status_messages = {
            "search": "",
            "analysis": "",
            "saving": ""
        }

    def get_renderables(self):
        """Customize the progress display to include status messages"""
        tasks = self.tasks.copy()
        if not tasks:
            return []

        renderables = []
        
        # Group progress bars with their status messages
        for task in tasks:
            # Add the progress bar
            renderables.append(self.make_tasks_table([task]))
            
            # Add the corresponding status message based on task type
            if task.description.lower().startswith("[blue]search") and self.status_messages["search"]:
                renderables.append(f"    └─> {self.status_messages['search']}\n")
            elif task.description.lower().startswith("[green]analysis") and self.status_messages["analysis"]:
                renderables.append(f"    └─> {self.status_messages['analysis']}\n")
            elif task.description.lower().startswith("[yellow]saving") and self.status_messages["saving"]:
                renderables.append(f"    └─> {self.status_messages['saving']}\n")

        return renderables

class ProgressLogHandler(logging.Handler):
    """Handles log messages and updates progress based on them"""
    def __init__(self, progress: StatusProgress):  # Removed tracker requirement
        super().__init__()
        self.progress = progress
        self.start_time = datetime.now()
        
        # Initialize tasks
        self.search_task = self.progress.add_task("[blue]Search Phase", total=100)
        self.analysis_task = self.progress.add_task("[green]Analysis Phase", total=100)
        self.saving_task = self.progress.add_task("[yellow]Saving Phase", total=100)
        
        # Initialize tracking variables
        self.total_topics = 5
        self.completed_topics = 0
        self.completed_papers = 0
        self.papers_found = 0
        self.current_topic = None
        self.current_phase = "search"
        
        # Progress tracking dictionaries
        self.search_progress = {
            "topics_generated": False,
            "queries_generated": False,
            "papers_found": False,
            "titles_checked": False,
            "abstracts_checked": False
        }
        
        self.analysis_progress = {
            "papers_analyzed": 0,
            "summary_generated": False,
            "new_research_generated": False
        }

    def emit(self, record: logging.LogRecord):
        """Process each log message and update progress accordingly"""
        try:
            if datetime.fromtimestamp(record.created) < self.start_time:
                return
                
            msg = record.getMessage()
            
            # Search Phase Updates
            if "Extracting research topics:" in msg:
                self.search_progress["topics_generated"] = True
                self._update_search_progress(20)
                self.progress.status_messages["search"] = "Generating research topics..."
                
            elif "Generating search queries for" in msg:
                self.search_progress["queries_generated"] = True
                self._update_search_progress(40)
                self.progress.status_messages["search"] = "Generating search queries..."
                match = re.search(r"(\d+) research topics", msg)
                if match:
                    self.total_topics = int(match.group(1))
                
            elif "Getting papers for" in msg:
                self.search_progress["papers_found"] = True
                self._update_search_progress(60)
                self.progress.status_messages["search"] = "Searching for papers..."
                
            elif "Checking relevence of" in msg and "papers for" in msg:
                if not self.search_progress["titles_checked"]:
                    self.search_progress["titles_checked"] = True
                    self._update_search_progress(80)
                topic = re.search(r"papers for (.+?)\.{3}", msg)
                if topic:
                    self.progress.status_messages["search"] = f"Checking relevance for topic: {topic.group(1)}"
                
            elif "Checking abstract relevence of" in msg:
                topic = re.search(r"papers for (.+?)\.{3}", msg)
                if topic:
                    self.progress.status_messages["search"] = f"Checking abstracts for topic: {topic.group(1)}"
                paper_count = re.search(r"of (\d+) papers", msg)
                if paper_count:
                    self.papers_found = int(paper_count.group(1))
                if not self.search_progress["abstracts_checked"]:
                    self.search_progress["abstracts_checked"] = True
                    self._update_search_progress(100)
                
            # Analysis Phase Updates
            elif "Research finished starting analysis:" in msg:
                self.current_phase = "analysis"
                self._update_search_progress(100)
                self.progress.status_messages["analysis"] = "Starting analysis..."
                
            elif "Analyzing paper:" in msg:
                self.analysis_progress["papers_analyzed"] += 1
                progress = min(60, (self.analysis_progress["papers_analyzed"] * 20))
                self._update_analysis_progress(progress)
                paper_title = msg.split("Analyzing paper: ")[1]
                self.progress.status_messages["analysis"] = f"Analyzing: {paper_title}"
                
            elif "Generating topic summary for topic:" in msg:
                if not self.analysis_progress["summary_generated"]:
                    self.analysis_progress["summary_generated"] = True
                    self._update_analysis_progress(80)
                topic = msg.split("for topic: ")[1]
                self.progress.status_messages["analysis"] = f"Generating summary for: {topic}"
                
            elif "Research analysis finished:" in msg:
                self.analysis_progress["new_research_generated"] = True
                self._update_analysis_progress(100)
                self.progress.status_messages["analysis"] = "Analysis complete"
                
            # Saving Phase Updates
            elif "Saving research results" in msg:
                self.current_phase = "saving"
                self._update_saving_progress(50)
                self.progress.status_messages["saving"] = "Saving research results..."
                
            elif "Analysis finished saving results:" in msg:
                self._update_saving_progress(100)
                self.progress.status_messages["saving"] = "Save complete"
                
        except Exception as e:
            print(f"Error in progress tracking: {e}")
            
    def _update_search_progress(self, target_progress: float):
        """Update search progress smoothly"""
        current = self.progress.tasks[self.search_task].completed
        if current < target_progress:
            self.progress.update(self.search_task, completed=target_progress)
            
    def _update_analysis_progress(self, target_progress: float):
        """Update analysis progress smoothly"""
        current = self.progress.tasks[self.analysis_task].completed
        if current < target_progress:
            self.progress.update(self.analysis_task, completed=target_progress)
            
    def _update_saving_progress(self, target_progress: float):
        """Update saving progress smoothly"""
        current = self.progress.tasks[self.saving_task].completed
        if current < target_progress:
            self.progress.update(self.saving_task, completed=target_progress)

def setup_logging_for_progress():
    """Setup logging with file rotation for a new research session"""
    log_directory = 'logs'
    if not os.path.exists(log_directory):
        os.makedirs(log_directory)
        
    log_files = [
        'llm_search.log', 
        'llm_analyzer.log', 
        'utils.log', 
        'llm_wrapper.log',
        'research_assistant.log'
    ]
    
    for log_file in log_files:
        file_path = os.path.join(log_directory, log_file)
        if os.path.exists(file_path):
            open(file_path, 'w').close()