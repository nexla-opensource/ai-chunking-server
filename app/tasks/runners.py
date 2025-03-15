import asyncio
import json
from pathlib import Path
from typing import Dict, Any, List
from app.tasks.base import BaseTaskRunner
from app.parsers.parser_factory import ParserFactory
from app.core.logging import get_logger

logger = get_logger("tasks.runners")


class ChunkingTaskRunner(BaseTaskRunner):
    """Runner for chunking tasks"""
    
    async def _execute(self, files: List[str], strategy: str = "default") -> Dict[str, Any]:
        """Execute a chunking task"""
        logger.info(f"Starting chunking task with {len(files)} files")
        results = []
        errors = []
        parsed_files_paths = []
        for file_path in files:
            try:
                logger.debug(f"Processing file: {file_path}")

                if file_path.endswith('.pdf'):
                    # Get appropriate parser for the file
                    parser = ParserFactory.get_parser(file_path)
                    
                    # Parse the file
                    output_path = parser.parse()
                    parsed_files_paths.append(output_path)
                else:
                    parsed_files_paths.append(file_path)
                logger.debug(f"Successfully processed file: {file_path}")
                
            except Exception as e:
                logger.error(f"Error processing file {file_path}: {str(e)}")
                errors.append({
                    "file_path": file_path,
                    "error": str(e),
                    "status": "failed"
                })
        
        base_dir = Path("/tmp/ai_chunking")
        task_dir = base_dir / self.task_result.task_id
        task_dir.mkdir(parents=True, exist_ok=True)

        from ai_chunking import RecursiveTextSplitter, SectionBasedSemanticChunker, SemanticTextChunker 

        # Chunk the file
        print("Strategy: ", strategy)
        if strategy == "default":
            strategy = "auto_ai"

        if strategy == "auto_ai":
            pass
        elif strategy == "section_semantic":
            chunker = SectionBasedSemanticChunker()
        elif strategy == "semantic":
            chunker = SemanticTextChunker() 
        elif strategy == "recursive_text":
            chunker = RecursiveTextSplitter(
                chunk_size=1000,
                chunk_overlap=100,
            )
        
        chunks = chunker.chunk_documents(parsed_files_paths)

        # Save the chunks to a JSON file based on the task_id
        with open(f"{task_dir}/chunks.json", "w") as f:
            json.dump([chunk.model_dump() for chunk in chunks], f, indent=4)

        results.append({
            "files_paths": files,
            "parsed_files_paths": parsed_files_paths,
            "chunks_file_path": f"{task_dir}/chunks.json",
            "status": "success"
        })

        final_result = {
            "processed_files": len(files),
            "successful": len(results),
            "failed": len(errors),
            "results": results,
            "errors": errors
        }
        
        logger.info(f"Completed chunking task. Processed: {len(files)}, Success: {len(results)}, Failed: {len(errors)}")
        return final_result 
