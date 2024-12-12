# progress/__init__.py

# Import everything needed from progress_tracking
from .progress_tracking import (
    ResearchStage,
    ProgressEvent,
    ProgressTracker,
    ResearchProgressMonitor
)

# Import everything needed from log_process
from .log_process import (
    StatusProgress,
    ProgressLogHandler,
    setup_logging_for_progress
)

# Define what should be available when using "from progress import *"
__all__ = [
    # From progress_tracking
    'ResearchStage',
    'ProgressEvent',
    'ProgressTracker',
    'ResearchProgressMonitor',
    
    # From log_process
    'StatusProgress',
    'ProgressLogHandler',
    'setup_logging_for_progress'
]

# Package metadata
__version__ = '1.0.0'
__author__ = 'Nickolas Goodis'
__description__ = 'Progress tracking for research assistant'