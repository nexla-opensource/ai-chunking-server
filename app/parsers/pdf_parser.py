import os
import json
import logging
import subprocess
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple

from app.core.logging import get_logger

logger = get_logger(__name__)

class PDFParser:
    def __init__(self, pdf_path: str):
        self.pdf_path = pdf_path
        if not os.path.exists(self.pdf_path):
            raise FileNotFoundError(f"PDF file not found: {self.pdf_path}")
        self.output_dir = os.path.dirname(self.pdf_path)
        self.output_path = pdf_path.replace(".pdf", ".md")
    
    def parse(
            self, 
            model_name: str = "gemini-2.0-flash",
            disable_image_extraction: bool = False,
            debug: bool = True,
            page_range: Optional[str] = None,
            force_ocr: bool = False,
            strip_existing_ocr: bool = False
        ) -> str:
        logger.info(f"Parsing PDF: {self.pdf_path}")
        
        gemini_api_key = os.getenv("GEMINI_API_KEY")
        if not gemini_api_key:
            raise ValueError("gemini_api_key is required for parsing PDFs")

        # Construct the CLI command
        command = [
            "marker_single",
            self.pdf_path,
            "--output_dir", self.output_dir,
            "--output_format", "markdown",
            "--use_llm",
            "--gemini_api_key", gemini_api_key,
            "--model_name", model_name
        ]

        if disable_image_extraction:
            command.append("--disable_image_extraction")
        if debug:
            command.append("--debug")
        if page_range:
            command.extend(["--page_range", page_range])
        if force_ocr:
            command.append("--force_ocr")
        if strip_existing_ocr:
            command.append("--strip_existing_ocr")

        try:    
            # Run the command with live output streaming
            logger.info(f"Running command: {' '.join(command)}")
            process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True
            )

            # Stream output in real-time
            while True:
                # Read stdout
                stdout_line = process.stdout.readline()
                if stdout_line:
                    logger.info(stdout_line.strip())

                # Read stderr
                stderr_line = process.stderr.readline()
                if stderr_line:
                    logger.error(stderr_line.strip())

                # Check if process has finished
                if process.poll() is not None:
                    # Read any remaining output
                    for line in process.stdout.readlines():
                        if line:
                            logger.info(line.strip())
                    for line in process.stderr.readlines():
                        if line:
                            logger.error(line.strip())
                    break

            # Check return code
            if process.returncode != 0:
                raise subprocess.CalledProcessError(process.returncode, command)
            
            # Check if output file exists
            if not os.path.exists(self.output_path):
                raise RuntimeError(f"Output file not created: {self.output_path}")

        except Exception as e:
            logger.error(f"Error parsing PDF: {str(e)}")
        
        # Return Markdown file path
        markdown_file_path = os.path.join(self.output_dir, os.path.basename(self.pdf_path).rsplit(".", 1)[0], os.path.basename(self.pdf_path).replace(".pdf", ".md"))
        return markdown_file_path
