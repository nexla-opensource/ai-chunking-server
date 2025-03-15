from abc import ABC, abstractmethod
from typing import Dict, Any, Tuple

class BaseParser(ABC):
    """Base class for all file parsers"""
    
    def __init__(self, file_path: str):
        self.file_path = file_path
        
    @abstractmethod
    def parse(self, **kwargs) -> str:
        """
        Parse the file and return the output file path
        
        Args:
            **kwargs: Additional parser-specific arguments
            
        Returns:
            str: Path to the output file
        """
        pass 