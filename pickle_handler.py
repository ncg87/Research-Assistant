import pickle
from typing import Any, Optional
from pathlib import Path
import os

def save_object(obj: Any, filepath: str, protocol: Optional[int] = None) -> bool:
    """
    Save an object to a file using pickle with error handling.
    
    Args:
        obj: Any Python object to be saved
        filepath: Path where the object should be saved
        protocol: Pickle protocol version (None uses highest available)
    
    Returns:
        bool: True if save was successful, False otherwise
    """
    try:
        # Create directory if it doesn't exist
        Path(filepath).parent.mkdir(parents=True, exist_ok=True)
        
        # Open file in binary write mode
        with open(filepath, 'wb') as file:
            pickle.dump(obj, file, protocol=protocol)
        return True
        
    except (pickle.PicklingError, PermissionError, OSError) as e:
        print(f"Error saving object: {str(e)}")
        return False

def load_object(filepath: str, default: Any = None) -> Any:
    """
    Load a pickled object from a file with error handling.
    
    Args:
        filepath: Path to the pickled file
        default: Value to return if loading fails
        
    Returns:
        The unpickled object or default value if loading fails
    """
    try:
        if not os.path.exists(filepath):
            print(f"File not found: {filepath}")
            return default
            
        with open(filepath, 'rb') as file:
            return pickle.load(file)
            
    except (pickle.UnpicklingError, EOFError, PermissionError, OSError) as e:
        print(f"Error loading object: {str(e)}")
        return default

# Example usage with your Research classes
def save_research_state(research_state: 'AnalysisResult', filepath: str) -> bool:
    """
    Save the research analysis state to a file.
    
    Args:
        research_state: AnalysisResult object to save
        filepath: Path where to save the state
        
    Returns:
        bool: True if save was successful
    """
    return save_object(research_state, filepath)

def load_research_state(filepath: str) -> Optional['AnalysisResult']:
    """
    Load the research analysis state from a file.
    
    Args:
        filepath: Path to the saved state file
        
    Returns:
        AnalysisResult object if successful, None otherwise
    """
    return load_object(filepath)