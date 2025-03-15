import os
from typing import Type
from .base_parser import BaseParser
from .pdf_parser import PDFParser

class ParserFactory:
    """Factory class for creating file parsers based on file extensions"""
    
    # Map of file extensions to parser classes
    _parsers = {
        '.pdf': PDFParser,
        # Add more parsers here as they are implemented
        # '.docx': DocxParser,
        # '.txt': TextParser,
        # etc.
    }
    
    @classmethod
    def get_parser(cls, file_path: str) -> BaseParser:
        """
        Get the appropriate parser for a given file path
        
        Args:
            file_path: Path to the file to be parsed
            
        Returns:
            BaseParser: An instance of the appropriate parser
            
        Raises:
            ValueError: If no parser is available for the file extension
        """
        _, ext = os.path.splitext(file_path)
        ext = ext.lower()
        
        parser_class = cls._parsers.get(ext)
        if parser_class is None:
            supported_formats = ', '.join(cls._parsers.keys())
            raise ValueError(
                f"No parser available for extension '{ext}'. "
                f"Supported formats are: {supported_formats}"
            )
        
        return parser_class(file_path)
    
    @classmethod
    def register_parser(cls, extension: str, parser_class: Type[BaseParser]) -> None:
        """
        Register a new parser for a file extension
        
        Args:
            extension: File extension (including the dot, e.g. '.pdf')
            parser_class: Parser class to handle this extension
        """
        cls._parsers[extension.lower()] = parser_class 