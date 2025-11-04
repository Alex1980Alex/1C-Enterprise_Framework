"""
BSL Indexer with Multiprocessing
Optimized for AMD Ryzen 7 5700G (16 threads)

Ожидаемое ускорение: 5-6x vs threading approach
"""

import sys
import json
import time
import logging
from pathlib import Path
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
from concurrent.futures import ProcessPoolExecutor, as_completed
from multiprocessing import cpu_count

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/multiprocess_indexing.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


@dataclass
class IndexingResult:
    """Result of indexing a single file"""
    file_path: str
    status: str  # success, failed, empty, error
    embedding: Optional[List[float]] = None
    metadata: Optional[Dict] = None
    error: Optional[str] = None
    processing_time_ms: Optional[float] = None


def process_file_worker(file_path: str, ollama_timeout: int = 90, use_cache: bool = True) -> Dict:
    """
    Worker function that processes a single file
    Runs in separate process to bypass GIL

    Args:
        file_path: Path to BSL file
        ollama_timeout: Timeout for Ollama embedding generation
        use_cache: Whether to use embedding cache

    Returns:
        Dictionary with processing result
    """
    start_time = time.time()

    try:
        # Import inside worker to avoid pickle issues
        from utils.bsl_parser import BSLParser
        from services.embedding_service import EmbeddingService
        from services.embedding_cache import EmbeddingCache

        # Initialize services (separate instance per process)
        parser = BSLParser()
        embedding_service = EmbeddingService(
            ollama_host="http://localhost:11434",
            model="nomic-embed-text:latest",
            cache_embeddings=False,  # Use our custom cache instead
            timeout=ollama_timeout
        )

        # Initialize cache if enabled
        cache = EmbeddingCache() if use_cache else None

        # Check cache first
        if cache:
            cached_data = cache.get(file_path)
            if cached_data:
                # Return cached result instantly
                return {
                    'file_path': file_path,
                    'status': 'success',
                    'embedding': cached_data['embedding'],
                    'metadata': cached_data.get('metadata', {}),
                    'processing_time_ms': (time.time() - start_time) * 1000,
                    'cached': True
                }

        # Parse file
        metadata = parser.parse_file(file_path)

        if not metadata or not metadata.functions:
            return {
                'file_path': file_path,
                'status': 'empty',
                'processing_time_ms': (time.time() - start_time) * 1000
            }

        # Create searchable text
        searchable_text = parser.extract_searchable_text(metadata)

        # Generate embedding
        embedding = embedding_service.create_embedding(searchable_text)

        if not embedding:
            return {
                'file_path': file_path,
                'status': 'failed',
                'error': 'Failed to create embedding',
                'processing_time_ms': (time.time() - start_time) * 1000
            }

        processing_time = (time.time() - start_time) * 1000

        # Prepare metadata
        result_metadata = {
            'module_type': metadata.module_type,
            'functions_count': len(metadata.functions),
            'variables_count': len(metadata.variables),
            'searchable_text': searchable_text[:500]  # First 500 chars
        }

        # Cache the result
        if cache:
            cache.put(file_path, embedding, result_metadata)

        return {
            'file_path': file_path,
            'status': 'success',
            'embedding': embedding,
            'metadata': result_metadata,
            'processing_time_ms': processing_time,
            'cached': False
        }

    except Exception as e:
        return {
            'file_path': file_path,
            'status': 'error',
            'error': str(e),
            'processing_time_ms': (time.time() - start_time) * 1000
        }


class MultiprocessIndexer:
    """
    Multiprocess indexer optimized for multi-core CPUs

    Features:
    - Uses ProcessPoolExecutor to bypass Python GIL
    - Configurable worker count (default: CPU cores - 4)
    - Progress tracking and statistics
    - Error handling and retry logic
    - Result saving in JSON format
    """

    def __init__(
        self,
        source_path: str,
        output_path: str = "data/index",
        max_workers: Optional[int] = None,
        ollama_timeout: int = 90,
        max_files: Optional[int] = None,
        use_cache: bool = True
    ):
        self.source_path = Path(source_path)
        self.output_path = Path(output_path)
        self.output_path.mkdir(parents=True, exist_ok=True)

        # Calculate optimal worker count
        if max_workers is None:
            # Use 75% of CPU threads (leave some for system + Ollama)
            cpu_threads = cpu_count()
            self.max_workers = max(1, cpu_threads - 4)
        else:
            self.max_workers = max_workers

        self.ollama_timeout = ollama_timeout
        self.max_files = max_files
        self.use_cache = use_cache

        logger.info(f"Initialized MultiprocessIndexer:")
        logger.info(f"  CPU threads: {cpu_count()}")
        logger.info(f"  Workers: {self.max_workers}")
        logger.info(f"  Source: {source_path}")
        logger.info(f"  Output: {output_path}")
        logger.info(f"  Caching: {'Enabled' if use_cache else 'Disabled'}")

    def get_files(self) -> List[Path]:
        """Get list of BSL files to process"""
        all_files = list(self.source_path.rglob("*.bsl"))

        if self.max_files:
            all_files = all_files[:self.max_files]

        logger.info(f"Found {len(all_files)} BSL files to process")
        return all_files

    def process_files(self, files: List[Path]) -> List[Dict]:
        """
        Process files using multiprocessing

        Args:
            files: List of file paths to process

        Returns:
            List of processing results
        """
        total_files = len(files)
        results = []
        start_time = time.time()

        logger.info(f"Starting multiprocess indexing with {self.max_workers} workers")
        logger.info(f"Processing {total_files} files...")

        with ProcessPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all tasks
            future_to_file = {
                executor.submit(process_file_worker, str(file), self.ollama_timeout, self.use_cache): file
                for file in files
            }

            # Collect results as they complete
            completed = 0
            for future in as_completed(future_to_file):
                file = future_to_file[future]

                try:
                    result = future.result(timeout=150)  # 2.5 min timeout
                    results.append(result)
                    completed += 1

                    # Progress update every 5 files
                    if completed % 5 == 0:
                        elapsed = time.time() - start_time
                        rate = completed / elapsed if elapsed > 0 else 0
                        eta = (total_files - completed) / rate if rate > 0 else 0

                        logger.info(
                            f"Progress: {completed}/{total_files} ({completed/total_files*100:.1f}%) | "
                            f"Speed: {rate:.2f} files/sec | "
                            f"ETA: {eta/60:.1f} min"
                        )

                except Exception as e:
                    logger.error(f"Exception processing {file}: {e}")
                    results.append({
                        'file_path': str(file),
                        'status': 'exception',
                        'error': str(e)
                    })
                    completed += 1

        total_time = time.time() - start_time
        logger.info(f"Completed processing {total_files} files in {total_time/60:.1f} minutes")

        return results

    def save_results(self, results: List[Dict], output_file: str = "index_multiprocess.json"):
        """Save results to JSON file"""

        # Calculate statistics
        stats = {
            'success': sum(1 for r in results if r['status'] == 'success'),
            'failed': sum(1 for r in results if r['status'] == 'failed'),
            'empty': sum(1 for r in results if r['status'] == 'empty'),
            'error': sum(1 for r in results if r['status'] == 'error'),
            'total': len(results)
        }

        # Calculate average processing time
        processing_times = [
            r['processing_time_ms']
            for r in results
            if 'processing_time_ms' in r and r['processing_time_ms'] is not None
        ]
        avg_time = sum(processing_times) / len(processing_times) if processing_times else 0

        # Create output
        output = {
            'metadata': {
                'created_at': datetime.now().isoformat(),
                'total_files': len(results),
                'embedding_model': 'nomic-embed-text:latest',
                'embedding_dimension': 768,
                'max_workers': self.max_workers,
                'cpu_threads': cpu_count(),
                'avg_processing_time_ms': avg_time,
                'indexing_stats': stats
            },
            'files': [
                {
                    'file_path': r['file_path'],
                    'status': r['status'],
                    'embedding': r.get('embedding'),
                    'metadata': r.get('metadata'),
                    'error': r.get('error'),
                    'processing_time_ms': r.get('processing_time_ms')
                }
                for r in results
                if r['status'] == 'success'  # Save only successful results
            ]
        }

        output_path = self.output_path / output_file

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(output, f, ensure_ascii=False, indent=2)

        logger.info(f"Results saved to: {output_path}")
        logger.info(f"Statistics:")
        logger.info(f"  Success: {stats['success']}")
        logger.info(f"  Failed: {stats['failed']}")
        logger.info(f"  Empty: {stats['empty']}")
        logger.info(f"  Error: {stats['error']}")
        logger.info(f"  Average time: {avg_time:.1f} ms per file")

    def run(self):
        """Main entry point"""
        logger.info("=" * 60)
        logger.info("BSL MULTIPROCESS INDEXER")
        logger.info("=" * 60)

        # Get files
        files = self.get_files()

        if not files:
            logger.warning("No files found to process!")
            return

        # Process files
        results = self.process_files(files)

        # Save results
        self.save_results(results)

        logger.info("=" * 60)
        logger.info("INDEXING COMPLETE")
        logger.info("=" * 60)


def main():
    """CLI entry point"""
    import argparse

    parser = argparse.ArgumentParser(
        description="BSL Multiprocess Indexer - Optimized for multi-core CPUs"
    )
    parser.add_argument(
        "source",
        help="Path to source directory containing BSL files"
    )
    parser.add_argument(
        "--output",
        default="data/index",
        help="Output directory for index files (default: data/index)"
    )
    parser.add_argument(
        "--max-workers",
        type=int,
        default=None,
        help="Maximum worker processes (default: CPU cores - 4)"
    )
    parser.add_argument(
        "--ollama-timeout",
        type=int,
        default=90,
        help="Timeout for Ollama requests in seconds (default: 90)"
    )
    parser.add_argument(
        "--max-files",
        type=int,
        default=None,
        help="Maximum number of files to process (for testing)"
    )

    args = parser.parse_args()

    indexer = MultiprocessIndexer(
        source_path=args.source,
        output_path=args.output,
        max_workers=args.max_workers,
        ollama_timeout=args.ollama_timeout,
        max_files=args.max_files
    )

    try:
        indexer.run()
    except KeyboardInterrupt:
        logger.info("\nInterrupted by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
